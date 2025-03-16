import numpy as np 
import glob,os
import soundfile as sf

def process_sounds(output_folder):
    def adjust_volume(signal, current_time, total_time, ref_distance=1.0, ref_level=0.0):
        # محاسبه فاصله (از ۱۰ متر به ۰ متر به صورت خطی)
        distance = 10 * (1 - current_time / total_time)
        
        # محاسبه تضعیف (attenuation) بر اساس فاصله
        attenuation = 20 * np.log10(distance / ref_distance)
        
        # محاسبه ضریب مقیاس (scale factor)
        scale_factor = 10 ** ((ref_level - attenuation) / 20)
        
        # اعمال تغییرات حجم صدا
        return signal * scale_factor
    def change_speed_numpy(data, speed_factor):
        indices = np.arange(0, len(data), speed_factor)
        indices = indices[indices < len(data)].astype(int)
        return data[indices]
    # نگاشت جهت‌ها به فایل‌های HRTF
    direct_mapping = {
        '0 deg': np.ones(10, dtype=np.int64) * 18,
        '45 deg': np.arange(9, -1, -1),
        '90 deg': np.ones(10, dtype=np.int64) * 0,
        '135 deg': np.arange(9, -1, -1),
        '180 deg': np.ones(10, dtype=np.int64) * 18,
        '225 deg': np.arange(27, 37, 1),
        '270 deg': np.ones(10, dtype=np.int64) * 36,
        '315 deg': np.arange(27, 37, 1),
    }

    # مقادیر سرعت
    speed_values = [0.5, 1.0, 1.5, 2.0]

    # مسیر فایل‌های HRTF و منبع صدا
    kemar_path = 'elev-10'
    source_path = 'source'
    Kemar = glob.glob(os.path.join(kemar_path, '*.wav'))
    Source = glob.glob(os.path.join(source_path, '*.wav'))
    Kemar.sort()

    # پردازش برای هر سرعت و هر فایل منبع
    for sp in speed_values:
        for sor in Source:
            # خواندن فایل منبع
            [sig, fs_s] = sf.read(sor)
            num_parts = 10
            length = len(sig)
            part_size = length // num_parts
            total_time = length / fs_s
            
            # تقسیم سیگنال به ۱۰ بخش
            segments = [sig[i * part_size:(i + 1) * part_size] for i in range(num_parts)]

            # پردازش برای هر جهت
            for deg, values in direct_mapping.items():
                mix = np.array([])
                (a, b) = (1, 0) if deg in ['135 deg', '180 deg', '225 deg'] else (0, 1)

                counter = 0
                for val in values:
                    # خواندن فایل HRTF
                    [HRTF, fs_H] = sf.read(Kemar[val])
                    current_time = (counter / num_parts) * total_time

                    # کانولوشن سیگنال با HRTF
                    s_L = np.convolve(segments[counter], HRTF[:, a], mode='full')
                    s_R = np.convolve(segments[counter], HRTF[:, b], mode='full')

                    # تنظیم حجم صدا بر اساس فاصله
                    s_R = adjust_volume(s_R, current_time, total_time)
                    s_L = adjust_volume(s_L, current_time, total_time)

                    # ترکیب سیگنال‌های چپ و راست
                    mix_n = np.vstack([s_L, s_R]).T

                    # اضافه کردن به میکس نهایی
                    mix = mix_n if mix.size == 0 else np.concatenate((mix, mix_n), axis=0)
                    counter += 1

                # تغییر سرعت سیگنال
                # num_samples = int(len(mix) / sp)
                # mix_sig = resample(mix, num_samples)
                # mix_sig = mix_sig / np.max(np.abs(mix_sig))  # نرمال‌سازی
                mix_sig = change_speed_numpy(mix, sp)
                # ذخیره فایل خروجی
                output_name = f"{os.path.splitext(os.path.basename(sor))[0]}_{deg}_{sp}x.wav"
                output_path = os.path.join(output_folder, output_name)
                sf.write(output_path, mix_sig, fs_s, format='WAV', subtype='PCM_16')

fol ="sounds"
path = os.path.join("assets",fol)
os.makedirs(path,exist_ok=True)
process_sounds(path)
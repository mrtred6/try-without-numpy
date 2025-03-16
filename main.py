from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
from pandas import DataFrame
import os,random, json
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime
from android.storage import primary_external_storage_path

path_font = os.path.join(os.path.dirname(__file__),"asset","STITRBD.ttf")
LabelBase.register(name='font', fn_regular = path_font)

class BaseScreen(Screen):
    def reshape_text(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    
    def show_popup(self, message):
        # نمایش پاپ‌آپ با پیام خطا
        popup = Popup(
            title="Error",
            content=Label(text=self.reshape_text(message)),
            size_hint=(0.5, 0.5)
        )
        popup.open()


class MainPage(BaseScreen):
    def btn(self):
        if self.ids.name.text =="":
            self.show_popup("اسم نمیتواند خالی باشد")
        else:
            Patient_name = self.ids.name.text
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H-%M")
            path_Patient = Patient_name + "_"+ formatted_time
            self.manager.patient_name_path = path_Patient
            self.manager.transition.direction = "left"  # تعیین جهت انیمیشن
            self.manager.current = "settings"  # تغییر صفحه

class SettingsPage(BaseScreen):
    def combine_lists(self, list1, list2, list3, n):
        random.shuffle(list3)
        result = []
        last_a = None  # آخرین مقدار انتخاب‌شده از list1
        
        for _ in range(n):
            a_choices = [a for a in list1 if a != last_a]  # جلوگیری از تکرار پشت سر هم در list1
            if not a_choices:
                a_choices = list1  # در صورت نیاز، لیست را مجدداً مجاز کن
            a = random.choice(a_choices)
            last_a = a  # به‌روزرسانی مقدار آخرین انتخاب

            b = random.choice(list2)
            c = random.choice(list3)  # بدون محدودیت برای مقدار c

            result.append(f"{a}_{b}_{c}.wav")
            
        return result

    selected_options_Suorce = []
    def SuorceBox(self, checkbox, value, option_id):
        options_map = {
            1: "Child",
            2: "Man formal",
            3: "Man informal",
            4: "Neutral",
            5: "Woman formal",
            6: "Woman informal"
        }

        option_text = options_map.get(option_id, "نامشخص")

        if value:
            self.selected_options_Suorce.append(option_text)  # اضافه کردن گزینه به لیست
        else:
            self.selected_options_Suorce.remove(option_text)


    selected_options_Ori = []
    def OriBox(self, checkbox, value, option_id):
        options_map = {
            1: "0 deg",
            2: "45 deg",
            3: "90 deg",
            4: "135 deg",
            5: "180 deg",
            6: "225 deg",
            7: "270 deg",
            8: "315 deg"
        }

        option_text = options_map.get(option_id, "نامشخص")

        if value:
            # بررسی اینکه تعداد انتخاب‌ها از 3 بیشتر نشود
            if len(self.selected_options_Ori) >= 4:
                checkbox.active = False  # غیرفعال کردن انتخاب جدید
                self.show_popup("شما نمی‌توانید بیش از چهار گزینه انتخاب کنید.")
            else:
                self.selected_options_Ori.append(option_text)  # اضافه کردن گزینه به لیست
        else:
            # حذف گزینه از لیست اگر غیرفعال شد
            if option_text in self.selected_options_Ori:
                self.selected_options_Ori.remove(option_text)

    selected_options_Speed =[]
    def SpeedBox(self, checkbox, value, option_id):
        options_map = {
            1: "0.5x",
            2: "1.0x",
            3: "1.5x",
            4: "2.0x",
        }

        option_text = options_map.get(option_id, "نامشخص")
        if value:
            self.selected_options_Speed.append(option_text)  # اضافه کردن گزینه به لیست
        else:
            self.selected_options_Speed.remove(option_text)
    def combine_list_string(self,lst, string):

        return [f"{item}*{string}" for item in lst]

    def btn(self):
        sel_Source=[]
        if any([
            self.ids.task_number.text in ["0", ""], not self.selected_options_Ori, 
            not self.selected_options_Speed, not self.selected_options_Suorce]):
            self.show_popup("هیچ کدام از مقادیر نمی تواند خالی باشد ")
        elif len(self.selected_options_Ori) < 4:
            self.show_popup("باید چهار جهت برای آزمون")
        else:
            for elm in self.selected_options_Suorce:
                # استفاده از یک دیکشنری برای نگهداری متناظر elm با self.ids.sorX
                source_mapping = {
                    "Child": self.ids.sor1,
                    "Man formal": self.ids.sor2,
                    "Man informal": self.ids.sor3,
                    "Neutral": self.ids.sor4,
                    "Woman formal": self.ids.sor5,
                }
                
                # اگر elm در دیکشنری وجود داشت، از آن استفاده کن، در غیر این صورت از sor6
                source_widget = source_mapping.get(elm, self.ids.sor6)
                
                # دریافت متن و تقسیم آن به لیست
                textinpulist = source_widget.text.split("\n")
                
                # ترکیب لیست با elm
                flist = self.combine_list_string(textinpulist, elm)
                
                # اضافه کردن عناصر flist به sel_Source (نه کل لیست flist)
                sel_Source.extend(flist)

            n = int(self.ids.task_number.text)
            self.manager.list_sound = self.combine_lists(
                sel_Source, 
                self.selected_options_Ori,
                self.selected_options_Speed, 
                n
            )
            self.manager.current = "start"

class StartPage(BaseScreen):
    def btn(self):
        self.manager.current = "first"

class FirstPage(BaseScreen):
    img = ObjectProperty(None)
    def on_enter(self):
        spl_list = self.manager.list_sound[0].split("*")
        
        esm = spl_list[0]
        self.manager.caracter = esm
        self.manager.list_sound[0] = spl_list[1]
        loc_list = self.manager.list_sound
        deg_sor = loc_list[0].split("_")[1]
        self.img.source = os.path.join(os.path.dirname(__file__),"assets","images" +deg_sor +".png")
        self.ids.my_label.text = self.reshape_text(esm)
  
    is_unlocked = False  
    attempts = 0  
    max_attempts = 5  # حداکثر تلاش مجاز

    def show_password_popup(self):
        if not self.is_unlocked and self.attempts < self.max_attempts:
            self.popup = Popup(title="Password Required", size_hint=(0.5, 0.4), auto_dismiss=False)
            
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            layout.add_widget(Label(text=self.reshape_text(" رمز عبور را وارد کنید:") , font_name='font'))
            
            self.password_input = TextInput(hint_text="Enter password", password=True, multiline=False)
            layout.add_widget(self.password_input)
            
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", spacing=10)
            close_btn = Button(text=self.reshape_text("بستن"), font_name='font', on_press=self.close_popup)
            submit_btn = Button(text=self.reshape_text("ادامه"), font_name='font', on_press=self.check_password)
            button_layout.add_widget(close_btn)
            button_layout.add_widget(submit_btn)
            
            layout.add_widget(button_layout)
            self.popup.content = layout
            self.popup.open()

    def check_password(self, instance):
        if self.password_input.text == "sbu123":  # رمز صحیح
            self.popup.dismiss()
            self.on_button_click()
        else:
            self.attempts += 1  # افزایش تعداد تلاش‌های ناموفق
            self.password_input.text = ""
            self.password_input.hint_text = f"Incorrect! {self.max_attempts - self.attempts} attempts left"

            if self.attempts >= self.max_attempts:  # اگر تعداد تلاش‌ها تمام شد
                self.popup.dismiss()
                self.disable_button()

    def close_popup(self, instance):
        self.popup.dismiss()

    def disable_button(self):
        self.ids.main_buttonl.text = self.reshape_text("غیر فعال شد")
        self.ids.main_button.disabled = True

    def on_button_click(self):
        self.manager.current = "last"

    def btn(self):
        self.manager.current = "contorl"
        self.manager.transition.direction = "left"
        self.manager.data_out["کاراکتر"].append(self.manager.caracter )

class ContorolPage(BaseScreen): 
    elapsed_time = 0.0  # مقدار ثانیه‌شمار
    running = False  # وضعیت تایمر

    def on_enter(self):
        loc_list = self.manager.list_sound
        direct = os.path.join(os.path.dirname(__file__),"sounds", loc_list[0] )  
        self.sound = SoundLoader.load(direct)
    def dis_save(self,stop_time, speed):
        total_time = 10/speed
        stop_distance = 10 * (1 - stop_time / total_time)
        self.manager.data_out["فاصله"].append(stop_distance)

    def start_timer(self):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.update_time, 0.01) 
            self.sound.play()
            self.ids.button1.opacity = 0  # Hide Button 1
            self.ids.button1.disabled = True  # Disable Button 1
            self.ids.button2.opacity = 1  # Show Button 2
            self.ids.button2.disabled = False  # Enable Button 2
            self.ids.lab2.text = self.reshape_text('توقف')
            self.ids.lab2.color = (170/255, 193/255, 209/255,1)
            self.ids.lab2.pos_hint = {'center_x':0.5, 'center_y':0.6}

    def stop_timer(self):
        if self.running:
            self.running = False
            Clock.unschedule(self.update_time)
            self.sound.stop()
            self.save_time()

    def update_time(self, dt):
        self.elapsed_time += dt

    def save_time(self):
        if not self.running:
            stop_time = round(self.elapsed_time, 2)
            self.manager.number_task +=1
            self.elapsed_time = 0.0
            loc_list =self.manager.list_sound[0].split("_")
            direction = loc_list[1].split(" ")[0]
            speed = float(loc_list[2][:-5])
            self.manager.data_out["مدت_زمان_ثانیه"].append(stop_time)
            self.manager.data_out["سرعت_پخش"].append(speed)
            self.manager.data_out["جهت_پخش_صدا"].append(direction)
            self.manager.data_out["منبع_صدا"].append(loc_list[0])
            self.manager.data_out["شماره_آزمون"].append(self.manager.number_task)
            self.Initial_state()
            self.dis_save(stop_time, speed)
            if len(self.manager.list_sound)==0:
                self.manager.current = "end"
            else:
                self.manager.current = "first"
    
    def Initial_state(self):
            self.ids.button1.opacity = 1  # Hide Button 1
            self.ids.button1.disabled = False  # Disable Button 1
            self.ids.button2.opacity = 0  # Show Button 2
            self.ids.button2.disabled = True  # Enable Button 2
            self.ids.lab2.text = self.reshape_text('شروع')
            self.ids.lab2.color = (5/255, 29/255, 53/255, 1)
            self.ids.lab2.pos_hint = {'center_x':0.5, 'center_y':0.4}
            del self.manager.list_sound[0]

class EndPage(BaseScreen):
    is_unlocked = False  
    attempts = 0  
    max_attempts = 5  # حداکثر تلاش مجاز

    def show_password_popup(self):
        if not self.is_unlocked and self.attempts < self.max_attempts:
            self.popup = Popup(title="Password Required", size_hint=(0.5, 0.4), auto_dismiss=False)
            
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            layout.add_widget(Label(text=self.reshape_text(" رمز عبور را وارد کنید:") , font_name='font'))
            
            self.password_input = TextInput(hint_text="Enter password", password=True, multiline=False)
            layout.add_widget(self.password_input)
            
            button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", spacing=10)
            close_btn = Button(text=self.reshape_text("بستن"), font_name='font', on_press=self.close_popup)
            submit_btn = Button(text=self.reshape_text("ادامه"), font_name='font', on_press=self.check_password)
            button_layout.add_widget(close_btn)
            button_layout.add_widget(submit_btn)
            layout.add_widget(button_layout)
            self.popup.content = layout
            self.popup.open()

    def check_password(self, instance):
        if self.password_input.text == "sbu123":  # رمز صحیح
            self.popup.dismiss()
            self.on_button_click()
        else:
            self.attempts += 1  # افزایش تعداد تلاش‌های ناموفق
            self.password_input.text = ""
            self.password_input.hint_text = f"Incorrect! {self.max_attempts - self.attempts} attempts left"

            if self.attempts >= self.max_attempts:  # اگر تعداد تلاش‌ها تمام شد
                self.popup.dismiss()
                self.disable_button()

    def close_popup(self, instance):
        self.popup.dismiss()

    def disable_button(self):
        self.ids.main_buttonl.text = self.reshape_text("غیر فعال شد")
        self.ids.main_button.disabled = True

    def on_button_click(self):
        self.manager.current = "last"

class LastPage(BaseScreen):
    def save_file(self):
        name = self.manager.patient_name_path
        folder = os.path.join(primary_external_storage_path(),"Download","Auditory Trust Test",name)
        os.makedirs(folder,exist_ok=True)
        namspl = name.split("_")
        user_info = {"نام": namspl[0],
            "تاریخ": namspl[1] ,  # فرمت استاندارد تاریخ
            "داده‌ها": self.manager.data_out}
        dir_file_csv = os.path.join(folder,name+".csv")
        df = DataFrame(self.manager.data_out)
        df.to_csv(dir_file_csv, index=False, encoding='utf-8-sig') 
        dir_file_jason = os.path.join(folder,name+".json") 
        with open(dir_file_jason, "w", encoding="utf-8") as f:
            json.dump(user_info, f, indent=4, ensure_ascii=False)

    def save_exit(self):
        self.save_file()
        App.get_running_app().stop()

    def save_continue(self):
        self.save_file()
        self.manager.number_task = 0
        self.manager.data_out = {key: [] for key in ["شماره_آزمون", "جهت_پخش_صدا", "سرعت_پخش", "فاصله", "مدت_زمان_ثانیه", "منبع_صدا"]}

        self.manager.transition.direction = "right"
        self.manager.current = "main"

    def exitAPP(self):
        App.get_running_app().stop()

class windowsmanager(ScreenManager):
    list_sound = ObjectProperty([])
    patient_name_path = "" 
    number_task = 0
    caracter = ''

kv = Builder.load_file('main.kv')
class AuditoryTrustTest(App):
    def build(self):
        self.icon="images/icon.png"
        Window.size = (1040, 650)
        return kv

if __name__ == "__main__":
    AuditoryTrustTest().run()

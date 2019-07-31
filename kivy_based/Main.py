from kivy.app import App
from kivy.uix import button as kb
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty

tempnum = NumericProperty('.25')

class Controller(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        smlist = ["one", "two"]
        for i in smlist:
            btn = Button(text=i,  size_hint_x=.25)
            btn.bind(on_press=self.callback)
            self.add_widget(btn)
            del btn

    def callback(self, instance):
        print('The button %s state is <%s>' % (instance, instance.state))

class TestApp(App):
    def build(self):
        return Controller()

if __name__ == '__main__':
    TestApp().run()
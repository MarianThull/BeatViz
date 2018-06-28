# coding=utf-8
__author__ = 'Dev'

from kivy.app import App
from kivy.uix.widget import Widget


class BeatViz(Widget):
    pass


class BeatVizApp(App):
    def build(self):
        return BeatViz()


if __name__ == "__main__":
    BeatVizApp().run()

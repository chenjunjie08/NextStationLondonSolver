import pyautogui
import cv2
import numpy as np
import time
import pdb


# while True:
#     screen = pyautogui.screenshot(region=(198, 613, 509, 1367))
#     screen = cv2.cvtColor(np.asarray(screen), cv2.COLOR_RGB2BGR)
#     target = cv2.imread('./Pics/sttn-08.png')
#     # target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

#     result = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
#     print(result.max())
#     time.sleep(1)


def img_check(screen, target):
    return cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED).max()


class Gui_input():
    def __init__(self) -> None:
        self.sttn = []
        self.power = []
        self.goal = []
        self.color = []

        for i in range(11):
            self.sttn.append(cv2.imread(f"./Pics/sttn-{i:02d}.png"))
        for i in range(4):
            self.power.append(cv2.imread(f"./Pics/power-{i:02d}.png"))
        for i in range(4):
            self.color.append(cv2.imread(f"./Pics/color-{i:02d}.png"))
        for i in range(5):
            self.goal.append(cv2.imread(f"./Pics/goal-{i:02d}.png"))

        self.mid = cv2.imread(f"./Pics/mid.png")

    @staticmethod
    def get_left_screen():
        screen = pyautogui.screenshot(region=(198, 613, 509, 1367))
        screen = cv2.cvtColor(np.asarray(screen), cv2.COLOR_RGB2BGR)
        return screen

    @staticmethod
    def get_mid_screen():
        screen = pyautogui.screenshot(region=(1210, 457, 707, 100))
        screen = cv2.cvtColor(np.asarray(screen), cv2.COLOR_RGB2BGR)
        return screen

    @staticmethod
    def get_right_screen():
        screen = pyautogui.screenshot(region=(2038, 580, 224, 308))
        screen = cv2.cvtColor(np.asarray(screen), cv2.COLOR_RGB2BGR)
        return screen

    def check_action(self):
        screen = self.get_mid_screen()
        return img_check(screen, self.mid) < 0.9

    def get_goals(self):
        screen = self.get_left_screen()
        res = []
        for goal in self.goal:
            res.append(img_check(screen, goal))
        res = np.array(res)
        res = np.where(res > 0.9)[0]
        if len(res) == 2:
            return res
        else:
            time.sleep(0.5)
            return self.get_goals()

    def get_power(self):
        screen = self.get_left_screen()
        res = []
        for power in self.power:
            res.append(img_check(screen, power))
        res = np.array(res)
        res = np.where(res > 0.9)[0]
        if len(res) == 1:
            return res[0]
        else:
            time.sleep(0.5)
            return self.get_power()

    def get_color(self):
        screen = self.get_right_screen()
        res = []
        for color in self.color:
            res.append(img_check(screen, color))
        res = np.array(res)
        res = np.where(res > 0.9)[0]
        if len(res) == 1:
            return res[0]
        else:
            time.sleep(0.5)
            return self.get_color()

    def get_sttn(self, card_used):
        screen = self.get_left_screen()
        res = []
        for sttn in self.sttn:
            res.append(img_check(screen, sttn))
        res = np.array(res)
        res = np.where(res > 0.9)[0]
        if len(res) == 1 and res[0] == 0:
            time.sleep(0.5)
            return self.get_sttn(card_used)
        elif len(res) > 0 and (res[0] not in card_used):
            return res
        else:
            time.sleep(0.5)
            return self.get_sttn(card_used)


if __name__ == '__main__':
    tmp = Gui_input()
    while True:
        print(tmp.get_sttn([]))
        time.sleep(0.5)

    # while True:
    #     x, y = pyautogui.position()
    #     print(x, y)

# -*- coding: utf-8 -*-

from tkinter import *
import datetime, itertools

import db, sensors

# Display resolution. Try to calculate it automatically or take from OS vars
X = 320
Y = 240

# Offset from phisical display border
global_padding = (3, 3, 3, 3) # pix

# Background color
global_bgnd_color = 'white'

class graf:
    def __init__(self, canvas, position_from, position_to, color = 'blue', border = 0, border_color = 0): #position in %
        self.canvas = canvas
        # position from to in pixels
        self.position_from = (int(position_from[0] * X), int(position_from[1] * Y))
        self.position_to = (int(position_to[0] * X), int(position_to[1] * Y))
        self.color = color
        self.W = self.position_from[0] - self.position_to[0]
        self.H = self.position_from[1] - self.position_to[1]
        if border_color == 0:
            border_color = self.color
        if border == 1:
            self.canvas.create_rectangle(self.position_from, self.position_to, outline = border_color)

    def add_title(self, text, position = (0,0), font = ('tahoma', 8), color = 0, tag = ''):
        if color == 0:
            color = self.color
        self.title_text = text
        self.title_position = (self.position_from[0] + position[0], self.position_from[1] + position[1])
        self.tit = self.canvas.create_text(self.title_position[0], self.title_position[1], text = self.title_text, fill=color, font=font, tags = tag)

    def add_graf(self, graf_padding, data, smooth = 0, border = 0, border_color = 0, tag = ''):
        self.data = data
        self.graf_point_start = (self.position_from[0] + graf_padding[3], self.position_from[1] + graf_padding[0])
        self.graf_point_end = (self.position_to[0] - graf_padding[1], self.position_to[1] - graf_padding[2])
        self.graf_H = self.graf_point_end[1] - self.graf_point_start[1]
        self.graf_W = self.graf_point_end[0] - self.graf_point_start[0]
        self.step_x = self.graf_W / len(data)
        self.step_y = (max(self.data.values()) - min(self.data.values())) / self.graf_H  # value in 1 pix
        self.graf_line = self.canvas.create_line(self.graf_data_prepar(self.data.values()), smooth=smooth, fill = self.color, tags = tag)
        if border_color == 0:
            border_color = self.color
        if border == 1:
            self.canvas.create_rectangle(self.graf_point_start, self.graf_point_end, outline = border_color)

    def step_y_update(self, data):
        self.step_y = (max(data.values()) - min(data.values())) / self.graf_H  # value in 1 pix

    def graf_data_prepar(self, d):
        graf_x = self.graf_point_start[0]
        data_ready = []
        for i in d:
            n = []
            n.append(int(graf_x))
            n.append(self.graf_point_end[1] - int((i - min(d)) / self.step_y))
            graf_x += self.step_x
            data_ready.append(n)
        return data_ready


    def add_x_axe(self, dash_length = 5, dash_shift = 4, x_dash_color = 0, x_lable_color = 0, x_lables_shift = (0,0), x_labels_font=('tahoma', 6), lables_number_limit = 24, x_lable_angle = 90):
        x_axe_lables_list = list(self.data.keys())
        x_dash_x = self.graf_point_start[0]
        y_dash_y = self.position_to[1]
        lable_filter = int(len(self.data) / lables_number_limit)
        if x_lable_color == 0:
            x_lable_color = self.color
        if x_dash_color == 0:
            x_dash_color = self.color
        count = 0
        for i in x_axe_lables_list:
            self.canvas.create_line(x_dash_x, y_dash_y + dash_shift, x_dash_x, y_dash_y + dash_shift - dash_length, fill = x_dash_color, tags = 'x_dashes')
            if count % lable_filter == 0:
                self.canvas.create_text(x_dash_x + x_lables_shift[0], y_dash_y + x_lables_shift[1], text = i, fill = x_lable_color, font = x_labels_font, angle = x_lable_angle, tags = 'x_labels')
            count += 1
            x_dash_x += self.step_x

    def add_y_axe(self, dash_length = 5, dash_shift = 4, y_dash_color = 0, y_lable_color = 0, y_lables_shift = (0,0), y_labels_font=('tahoma', 6)):
        min_y = min(self.data.values())
        max_y = max(self.data.values())
        y_axe_lables_list = list(range(int(min_y), int(max_y)+1))
        y_axe_lables_list.pop(0)
        x_dash_x = self.graf_point_start[0]
        y_dash_y = self.graf_point_end[1]
        if y_lable_color == 0:
            y_lable_color = self.color
        if y_dash_color == 0:
            y_dash_color = self.color
        for i in y_axe_lables_list:
            xf = x_dash_x + dash_shift
            yf = y_dash_y - int((i - min_y) / self.step_y)
            xt = x_dash_x + dash_shift + dash_length
            yt = y_dash_y - int((i - min_y) / self.step_y)
            self.canvas.create_line(xf, yf, xt, yt, fill = y_dash_color, tags = 'y_dashes')
            self.canvas.create_text(x_dash_x + y_lables_shift[0], yf + y_lables_shift[1], text = i, fill = y_lable_color, font = y_labels_font, tags = 'y_labels')
            y_dash_y += self.step_y
        print ('ups')



class Interface(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        # get data
        d = db.Gui_Data().get_temp_24h()

        t3 = Toplevel(self,  bg='gray')
        t3.overrideredirect(1)
        t3.geometry('%sx%s' % (X, Y)) # сделать определение разрешения экрана

        self.canvas = Canvas(t3, width = X, height= Y)

        curtime = datetime.datetime.now().strftime('%H:%M:%S')
        self.sensors = sensors.sensors()
        curtemp_out = 'Temp Out: %s' % round(self.sensors.read_temp_DS18B20(), 2)
        curtemp_in = 'Temp In: %s' % round(self.sensors.read_temp_BME280(), 2)

        self.temp = graf(self.canvas, (0,0), (1,1), border = 1, border_color = 'red')
        self.temp.add_graf((20,5,28,25), d, smooth = 1, border = 1, tag = 'graf_temp_out')
        self.temp.add_x_axe(4, dash_shift = -24, x_lables_shift=(0, -11), x_lable_color = 'dark slate gray', x_lable_angle = 90)
        self.temp.add_y_axe(300, dash_shift = -4, y_dash_color = 'SteelBlue2',  y_lables_shift=(-10, 0), y_labels_font=('tahoma', 8))
        self.temp.add_title(curtime, position = (50,10), font = ('tahoma', 9), color = 'green', tag = 'time')
        self.temp.add_title(curtemp_out, position = (265,10), font = ('tahoma', 9), color = 'red', tag = 'cur_temp_out')
        self.temp.add_title(curtemp_in, position = (150,10), font = ('tahoma', 9), color = 'purple', tag = 'cur_temp_in')
        self.canvas.pack()


        self.update_clock()
        self.update_graf()
        self.update_axes()
        self.update_cur_temp()

    def update_clock(self):
        curtime = datetime.datetime.now().strftime("%H:%M:%S")
        self.canvas.itemconfig("time", text = curtime)
        # call this function again in one second
        self.after(1000, self.update_clock)

    def update_cur_temp(self):
        curtemp_out = 'Temp Out: %s' % round(self.sensors.read_temp_DS18B20(), 2)
        curtemp_in = 'Temp In: %s' % round(self.sensors.read_temp_BME280(), 2)
        self.canvas.itemconfig("cur_temp_out", text = curtemp_out)
        self.canvas.itemconfig("cur_temp_in", text = curtemp_in)
        self.after(5000, self.update_cur_temp)

    def update_graf(self):
        fresh_data = db.Gui_Data().get_temp_24h()
        self.temp.step_y_update(fresh_data)
        prepar_data = self.temp.graf_data_prepar(list(fresh_data.values()))
        self.canvas.coords('graf_temp_out', *flatten(prepar_data))
        self.after(10000, self.update_graf)

    def update_axes(self):
        fresh_data = db.Gui_Data().get_temp_24h()
        self.temp.data = fresh_data
        self.canvas.delete("x_dashes", "y_dashes", "x_labels", "y_labels")
        self.temp.add_x_axe(4, dash_shift = -24, x_lables_shift=(0, -11), x_lable_color = 'dark slate gray', x_lable_angle = 90)
        self.temp.add_y_axe(300, dash_shift = -4, y_dash_color = 'SteelBlue2',  y_lables_shift=(-10, 0), y_labels_font=('tahoma', 8))

        self.after(30000, self.update_axes)



# from itertools recipes: https://docs.python.org/2/library/itertools.html
def flatten(list_of_lists):
    """Flatten one level of nesting"""
    return itertools.chain.from_iterable(list_of_lists)











#temp.title_text = 'Temperature, C ' + datetime.datetime.now().strftime('%H:%M:%S')







#### Color scheme

##day
##night


### Global
##background

### Graf
##background
##title
##x_axe_dash
##x_axe_lables
##y_axe_dash
##y_axe_lables = graf


#canvas.pack()

#root.mainloop()

#
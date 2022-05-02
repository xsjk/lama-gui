import tkinter as tk
from PIL import Image, ImageTk,ImageDraw
import os,asyncio,shutil
from tkinter import ttk,filedialog



BLACK = '#000000'
GREEN = '#FFFF00'
RED = '#FF0000'
BLUE = '#0000FF'


    




class MainWindow(tk.Tk):

    # 鼠标位置
    X = 0
    Y = 0
    
    # 缩放系数
    K = 1

    # 涂鸦半径
    R = 25
    R_max = 100


    processing = False
    def not_processing(self,f):
        def f_(*args,**kwargs):
            if not self.processing:
                return f(*args,**kwargs)
            print("processing")
        return f_


    history = []
    future = []

    root = os.path.dirname(__file__)
    temp = os.path.join(root, "temp")
    if os.path.exists(temp):
        shutil.rmtree(temp)
    os.mkdir(temp)
    model = os.path.join(root, "big-lama")
    img_name = 'res.png'
    


    def __init__(self):
        
        # 创建主窗口
        super(MainWindow, self).__init__()
        self.title('涂鸦')
        
        # 隐藏窗口
        self.withdraw()

        
        


        self.fr = tk.Frame(self)
        self.fr.pack(side=tk.RIGHT)

        @self.not_processing
        def process(event): 
            async_run(self.process())
        

        self.canvas2 = tk.Canvas(self.fr,width=2*self.R_max,height=2*self.R_max)
        self.canvas2.pack(padx=10, pady=10)
        self.canvas2.create_oval(self.R_max-self.R, self.R_max-self.R, self.R_max+self.R, self.R_max+self.R, fill='black')
        





        # 创建画布
        self.canvas = tk.Canvas(self)

        # 读取图片并创建画布
        while not (filename:=filedialog.askopenfilename(filetypes=[('PNG图片', '*.png'), ('JPEG图片', '*.jpg')])): pass
        self.open(filename)        
        
        #鼠标左键单击，画第一个点
        @self.not_processing
        def onLeftButtonDown(event):
            self.canvas.create_oval(event.x-self.R, event.y-self.R, event.x+self.R, event.y+self.R, fill='white', outline='white')
            self.draw.ellipse([(int((event.x-self.R)*self.K), int((event.y-self.R)*self.K)), (int((event.x+self.R)*self.K), int((event.y+self.R)*self.K))], fill='white', outline='white')
            (self.X,self.Y) = (event.x, event.y)
        
        #按住鼠标左键拖动，画图
        @self.not_processing
        def onLeftButtonMove(event):
            self.canvas.create_line([(self.X, self.Y), (event.x, event.y)], fill='white', width=self.R*2, capstyle=tk.ROUND,)
            self.draw.line([(int(self.X*self.K), int(self.Y*self.K)), (int(event.x*self.K), int(event.y*self.K))], fill='white', width=int(self.R*2*self.K))
            self.draw.ellipse([(int((event.x-self.R)*self.K), int((event.y-self.R)*self.K)), (int((event.x+self.R)*self.K), int((event.y+self.R)*self.K))], fill='white', outline='white')
            (self.X,self.Y) = (event.x, event.y)

        #鼠标滚轮，改变笔画粗细
        def onMouseWheel(event):
            delta = 1
            if event.delta>0 and self.R+delta<=self.R_max:
                self.R += delta
            elif event.delta<0 and self.R-delta>=0:
                self.R -= delta
            self.refresh_canvas2()
            
        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)



        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=int(self.width/self.K), mode='indeterminate', value=0)
        self.progressbar.start(10)








        @self.not_processing
        def save(event):
            filename = filedialog.asksaveasfilename(filetypes=[('PNG图片', '*.png')], defaultextension='.png')
            if '.png' not in filename:
                filename += '.png'
            print(f"save as {filename}")
            self.image.save(filename)
        
        @self.not_processing
        def open(event):
            filename = filedialog.askopenfilename(filetypes=[('PNG图片', '*.png')])
            self.K=1
            print(f"open {filename}")
            self.open(filename)
        
        @self.not_processing
        def undo(event):
            if len(self.history)>1:
                print("undo")
                self.future.append(self.history.pop())
                self.image = self.history[-1]
                self.load_img()
        
        @self.not_processing
        def redo(event):
            if len(self.future)>0:
                print("redo")
                self.history.append(self.future.pop())
                self.image = self.history[-1]
                self.load_img()
        
        @self.not_processing
        def scale(event):
            # scale the canvas and the image in it
            if event.delta<0:
                self.K += 0.1
            elif event.delta>0 and self.K>0.1:
                self.K -= 0.1
            
            self.load_img()
            pass

        
        self.bind_all('<Control-s>', save)
        self.bind_all('<Control-o>', open)
        self.bind_all('<Control-z>', undo)
        self.bind_all('<Control-y>', redo)
        self.bind_all('<Control-r>', lambda e:self.load_img())
        self.bind_all('<Control-q>', lambda e:self.destroy())
        self.bind_all('<Control-MouseWheel>',scale)
        self.canvas2.bind('<Button-1>', process)
        self.bind_all('<Button-3>',process)
        self.canvas.bind('<Button-1>', onLeftButtonDown)  #单击左键
        self.canvas.bind('<B1-Motion>', onLeftButtonMove)  #按住并移动左键
        self.canvas.bind_all('<MouseWheel>', onMouseWheel)  #滚轮放大缩小


        self.wm_deiconify()

    def refresh_canvas2(self):
        self.canvas2.config(width=int(self.R_max*2), height=int(self.R_max*2))
        self.canvas2.delete("all")
        self.canvas2.create_oval(int((self.R_max-self.R)), int((self.R_max-self.R)), int((self.R_max+self.R)), int((self.R_max+self.R)), fill='black')
    
    
    def open(self,filename):
        self.image = Image.open(filename)
        self.img_path = os.path.join(self.temp, self.img_name)
        self.mask_name = os.path.splitext(self.img_name)[0] + '_mask.png'
        self.mask_path = os.path.join(self.temp, self.mask_name)
        self.load_img()
        if self.width*1.5>self.winfo_screenwidth() or self.height*1.5>self.winfo_screenheight():
            self.K = max(self.width/self.winfo_screenwidth()*1.5, self.height/self.winfo_screenheight()*1.5)
            self.load_img()

        self.history.append(self.image)
        self.future.clear()

    

    
    def load_img(self):
        self.image.save(self.img_path)
        self.width, self.height = self.image.size
        self.imageTk = ImageTk.PhotoImage(self.image.resize((int(self.width/self.K), int(self.height/self.K))))
        self.canvas.create_image(int(self.width/self.K/2),int(self.height/self.K/2), image=self.imageTk)
        self.canvas.config(width=int(self.width/self.K), height=int(self.height/self.K))
        self.mask = Image.new("RGB", (self.width, self.height), BLACK)
        self.draw = ImageDraw.Draw(self.mask)            
        self.refresh_canvas2()
    

    async def process(self):
        self.processing = True

        self.progressbar.pack(expand=tk.YES,fill=tk.X,padx=1)
        self.canvas2.pack_forget()
        # self.canvas2.delete("all")

        self.mask.save(self.mask_path)
        
        print("Processing")
        command = ' '.join([
            "python", os.path.join(self.root, 'lama\\bin\\predict.py'),
            f"model.path={self.model}",
            f"indir={self.temp}",
            f"outdir={self.temp}",
            "device=cpu"
        ])
        
        c = os.system(command)
        if not c:
            print("success")
            self.open(self.mask_path)

        else:
            print("fail")


        self.progressbar.pack_forget()
        self.canvas2.pack(padx=10,pady=10)

        self.processing = False




    

    


from threading import Thread
def init(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
event_loop = asyncio.new_event_loop()                     # 创建异步事件循环对象——mainloop
t = Thread(target=init,args=(event_loop,))                # 创建线程对象（使得异步事件循环在其中执行）
t.start()                                               # 启动线程，即在该线程中启动异步主循环
def async_run(async_func):
    return asyncio.run_coroutine_threadsafe(async_func,event_loop) 



MainWindow().mainloop()


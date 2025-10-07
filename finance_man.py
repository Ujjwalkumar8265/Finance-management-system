import tkinter as tk
from tkinter import ttk,messagebox
import pymysql
class fina():
    def __init__(self ,root):
        self.root = root
        self.root.title("FINANCE MANAGEMENT DASHBOAD")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}")
        
        title = tk.Label(self.root , text="FINANCE MANAGEMENT ",bd=4,relief="groove", font=("Arial",50,"bold"),bg="light green")
        title.pack(side="top",fill="x")
        

        #frame

        addframe=tk.Frame(self.root,bd=5,relief="ridge",bg=self.col(200,210,180))
        addframe.place(width=450,height=660,x=80, y=100)

        #widgets 
        # for amount
        amountlabel=tk.Label(addframe, text="AMOUNT",bg=self.col(200,210,180),font=("Arial",15,"bold"))
        amountlabel.grid(row=0,column=0,padx=20,pady=30)
        self.amount=tk.Entry(addframe,bd=2,width=20, font=("arial",15))
        self.amount.grid(row=0,column=1,padx=10,pady=30)

        #type label
        typelabel=tk.Label(addframe, text="TYPE",bg=self.col(200,210,180),font=("Arial",15,"bold"))
        typelabel.grid(row=1,column=0,padx=20,pady=30)
        self.type=tk.Entry(addframe,bd=2,width=20, font=("arial",15))
        self.type.grid(row=1,column=1,padx=10,pady=30)

        #buttons
        #income button
        inbutton=tk.Button(addframe,command=self.incomefun,bd=2,relief="raised",width=20,font=("arial",20,"bold"),text="INCOME")
        inbutton.grid(row=2,column=0,padx=30,pady=40,columnspan=2)

        # expences button
        expbutton=tk.Button(addframe,command=self.expfun,bd=2,relief="raised",width=20,font=("arial",20,"bold"),text="EXPENCE")
        expbutton.grid(row=3,column=0,padx=30,pady=40,columnspan=2)

        #AUDIT BUTTON
        audbutton=tk.Button(addframe,command=self.auditfun,bd=2,relief="raised",width=20,font=("arial",20,"bold"),text="AUDIT")
        audbutton.grid(row=4,column=0,padx=30,pady=40,columnspan=2)

                       
        #details frames
        self.detaframe=tk.Frame(self.root, bd=5 , relief="ridge",bg=self.col(210,180,200))
        self.detaframe.place(width=self.width/2 ,height=660,x=self.width/3+160, y=100)

        lab=tk.Label(self.detaframe,text="AUDIT DETAILS",bd=3,relief="groove",bg=self.col(110,150,200),font=("arial",25,"bold"))
        lab.pack(side="top",fill="x")

        self.tabfun()

    def tabfun(self):
        tabframe=tk.Frame(self.detaframe,bd=5,relief="ridge",bg="cyan")
        tabframe.place(width=self.width/2-40,height=575,x=17,y=60)

        #scrollbar for screen
        #x scrool bar
        x_scrol=tk.Scrollbar(tabframe,orient="horizontal")
        x_scrol.pack(side="bottom",fill="x")

        # y scrool bar
        y_scrol=tk.Scrollbar(tabframe,orient="vertical")
        y_scrol.pack(side="right",fill="y") 

        self.table =ttk.Treeview(tabframe,xscrollcommand=x_scrol.set,yscrollcommand=y_scrol.set,columns=("company","Income","Expence","Audit"))
        x_scrol.config(command=self.table.xview)
        y_scrol.config(command=self.table.yview)
        self.table.heading("company",text="Company")        
        self.table.heading("Income",text="INCOME")
        self.table.heading("Expence",text="EXPENCE")
        self.table.heading("Audit",text="AUDIT")
        self.table["show"]="headings"
        self.table.pack(fill="both",expand=1)


    def incomefun(self):
        amount=self.amount.get()
        tp=self.type.get()

        if amount and tp:
            amount_int=int(amount)
            try:
                self.dbconnectfun()
                self.cur.execute("select income from finance where company='ABC'")
                row = self.cur.fetchone()
                upd = row[0]+amount_int
                self.cur.execute("update finance set income=%s where company='ABC'",upd)
                self.con.commit()
                tk.messagebox.showinfo("Success",f"{amount_int} amount of {tp} is added as income")
                self.tabfun()
                self.table.delete(*self.table.get_children())
                self.cur.execute("select * from finance where company='ABC'")
                data= self.cur.fetchone()
                self.table.insert('',tk.END,values=data)
                self.con.close()



            except Exception as e:
                tk.messagebox.showerror("Error",f"Error:{e}")     


        else:    
            tk.messagebox.showerror("Error","fill all input fields")   






    def col(self,r,g,b):
        return f"#{r:02x}{g:02x}{b:02x}" 

    def dbconnectfun(self):
        self.con=pymysql.connect(host="localhost",user="root",passwd="bhudave911@",database="rec")
        self.cur= self.con.cursor()

    def expfun(self):
        amount=self.amount.get()
        tp=self.type.get()
        if amount and tp:
            amount_int=int(amount)
            try:
                self.dbconnectfun()
                self.cur.execute("select expence from finance where company='ABC'")
                row=self.cur.fetchone()
                upd=row[0]+amount_int
                self.cur.execute("update finance set expence=%s where company='ABC'",upd)
                self.con.commit()
                tk.messagebox.showinfo("Success",f"{amount_int} amount of {tp} is added as income")
                self.tabfun()
                self.table.delete(*self.table.get_children())
                self.cur.execute("select * from finance where company='ABC'")
                data= self.cur.fetchone()
                self.table.insert('',tk.END,values=data)
                self.con.close()
            except Exception as e:
                tk.messagebox.showerror("Error",f"Error:{e}")
        else:
            tk.messagebox.showerror("Error","fill all input fields")


    def auditfun(self):
        try:
            self.dbconnectfun()
            self.cur.execute("select income, expence from finance where company='ABC'")
            data= self.cur.fetchone()
            inc= data[0]
            exp=data[1]
            audit=inc - exp
            self.cur.execute("update finance set balance=%s where company='ABC'" ,audit)
            self.con.commit()

            if audit>0:
                tk.messagebox.showinfo("Information","company is in profit")
            elif audit<0:
                tk.messagebox.showinfo("Information","company is in loss")        

            self.tabfun()
            self.table.delete(*self.table.get_children())
            self.cur.execute("select * from finance where company='ABC'")
            info= self.cur.fetchone()
            self.table.insert('',tk.END,values=info)


        except Exception as e:
            tk.messagebox.showerror("Error",f"Error:{e}")


root=tk.Tk()
obj = fina(root)
root.mainloop()
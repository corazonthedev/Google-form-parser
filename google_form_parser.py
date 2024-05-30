from bs4 import BeautifulSoup
from seleniumbase import SB
import os, re, json, logging, sys
from seleniumbase import BaseCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import tkinter as tk

if not os.path.exists("FORMS"): #check folder 
    os.mkdir("FORMS") #create DEPO folder
form_path = "FORMS\\"

#create logger
logger = logging.getLogger('parser_logger')
logger.setLevel(logging.DEBUG)
file_processor = logging.FileHandler('latest.log')
file_processor.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_processor.setFormatter(formatter)
logger.addHandler(file_processor)

url_no = -1 #TODO: for processing multiple links 
class TestParser(BaseCase):
    def ParserLauncher(self,reset):
        global root
        try:
            root.destroy()
        except:pass
        def toggle_password():
            if entry_user_password.cget('show') == '': entry_user_password.config(show='*')
            else:entry_user_password.config(show='')
        root = tk.Tk()
        root.title("Google form parser")
        root.geometry("400x400")
        
        if reset:text_user_email.delete(0, tk.END)

        text_user_email = tk.Label(root, text="enter your gmail:")
        text_user_email.pack(pady=5)
        entry_user_email = tk.Entry(root,width=30)
        entry_user_email.pack(pady=5)

        text_user_password = tk.Label(root, text="enter your gmail password:")
        text_user_password.pack(pady=5)
        entry_user_password = tk.Entry(root,show='*',width=30)
        entry_user_password.pack(pady=5)
        
        toggle_button = tk.Button(root, text="Show/Hide", command=toggle_password)
        toggle_button.pack(pady=5)

        text_user_link = tk.Label(root, text="enter target Google form url:")
        text_user_link.pack(pady=5)
        entry_user_link = tk.Entry(root,width=60)
        entry_user_link.pack(pady=5)
        
        submit_button = tk.Button(root, text="Submit", command= lambda: self.save_link(entry_user_email,entry_user_password,entry_user_link))
        submit_button.pack(pady=20)
        root.mainloop()
    
    def save_link(entry_mail,entry_pass,entry_link):
        global user_email, user_password, user_link
        user_email = entry_mail.get()
        user_password = entry_pass.get()
        user_link = entry_link.get()
        root.destroy()
        with open("link.txt", 'w') as file:
            file.write(user_link)
        with SB(uc=True, headless=True) as sb:   
            TestParser.check_account_link(sb,user_link,user_email,user_password)
    
    def check_account_link(self,link,email,password):
        self.open(link)
        if self.is_element_visible('input[type="email"][autocomplete="username"]'):
            self.type('input[type="email"]', email) #enter email
            self.click('div[id="identifierNext"]') #next
            self.wait_for_element_visible('input[type="password"]') #wait for password
            self.type('input[type="password"]', password) #enter password
            self.click('div[id="passwordNext"]') #next
            self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
            with SB(uc=True, headless=True) as sb:
                TestParser.parser(sb)
                print("parse finished")
                sys.exit()
        else: pass
        
    def parser(self): 
        global page_no,url_no, user_email, user_password, user_link
        with open("link.txt", "r") as f:
            for line in f: #MAINLOOP, #FIXME: although it's a loop unable to parse multiple forms - BUG may accure
                url_no += 1 
                if url_no == 1: break
                if line == "" or line == "\n": continue
                counter, page_no = 0, 0
                url = line.strip() #strip url
                self.open(url) #open
                self.sleep(3) #improve
                unparsable = False 
                try: #CHECK REQUIRE LOGIN POP-UP
                    self.execute_script('document.querySelector("body > div.llhEMd.iWO5td > div > div.g3VIld.Up8vH.J9Nfi.iWO5td > div.XfpsVe.J9fJmf > div.U26fgb.O0WRkf.oG5Srb.HQ8yf.C0oVfc.kHssdc.HvOprf.TFBnVe.M9Bg4d > span > span").click();')
                    logger.info(f'login pop-up on {url}')
                    self.wait_for_element_visible('input[type="email"][autocomplete="username"]')
                except: pass
                
                if self.is_element_visible('input[type="email"][autocomplete="username"]'): #CHECK LOGIN
                    self.type('input[type="email"]', user_email) #enter email
                    self.click('div[id="identifierNext"]') #next
                    self.wait_for_element_visible('input[type="password"]') #wait for password
                    self.type('input[type="password"]', user_password) #enter password
                    self.click('div[id="passwordNext"]') #next
                    self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
                    logger.info(f'logged in on {url}') #DEBUG
                    
                    while True: #parse every page
                        self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
                        counter += 1
                        if counter == 10:
                            logger.critical(f'10-loop parse fail on {url}') #DEBUG
                            break
                        if self.is_element_visible('div[jsname="M2UYVd"]'): #last page, SEND BUTTON
                            TestParser.do_parse(self)
                            logger.info(f'parse finish on {form_title}') #DEBUG
                            break #END
                            
                        else: #not last page, NEXT BUTTON
                            try: #CHECK UPDATE POP-UP
                                self.execute_script('document.querySelector("body > div.NBxL9e.iWO5td > div > div.I7OXgf.guoxt.ZEeHrd.Inn9w.iWO5td > div.OE6hId.J9fJmf > div > span > span").click();')
                                logger.info(f'update pop-up on {url}')
                            except: pass
                            TestParser.do_parse(self)
                            if self.is_element_visible('div[class="Qr7Oae"][role="listitem"]'):
                                TestParser.fill_form(self)
                            if self.is_element_visible('span[class="RHiWt"]'): #check any error
                                self.save_screenshot(f"FORMS\\{folder_form_title}\\unparsable{counter}.png")
                                logger.critical(f'unparsable {form_title}')
                                unparsable = True
                                break #END for i
                            else: #no error
                                self.click('div[jsname="OCpkoe"]') #next
                else: #NO LOGIN 
                    self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
                    logger.info(f'no login on {url}') #DEBUG
                    
                    while True: #parse every page
                        self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
                        counter += 1
                        if counter == 10:
                            logger.critical(f'10-loop parse fail on {url}') #DEBUG
                            break
                        try:
                            self.wait_for_element_visible('div[jsname="OCpkoe"]',timeout=5)
                        except:
                            self.wait_for_element_visible('div[jsname="M2UYVd"]',timeout=5)
                        if self.is_element_visible('div[jsname="M2UYVd"]'): #last page, SEND BUTTON
                            TestParser.do_parse(self)
                            logger.info(f'parse finish on {form_title}')
                            break #END
                        else: #not last page, NEXT BUTTON
                            TestParser.do_parse(self)
                            if self.is_element_visible('div[class="Qr7Oae"][role="listitem"]'):
                                TestParser.fill_form(self)
                            if self.is_element_visible('span[class="RHiWt"]'): #check any error
                                self.click('span[class="RHiWt"]')
                                self.save_screenshot(f"{folder_form_title}\\unparsable{counter}.png")
                                logger.critical(f'unparsable {form_title}')
                                unparsable = True
                                break #END for i
                            else: #no error
                                try:
                                    self.wait_for_element_clickable('div[jsname="OCpkoe"]')
                                    self.click('div[jsname="OCpkoe"]') #next
                                except Exception as err:
                                    logger.critical(err)
                                    self.save_screenshot(f"{folder_form_title}\\unparsable{counter}.png")
                
                if unparsable:
                    self.click('div[role="button"][jsname="X5DuWc"]') #clear form
                    self.execute_script('document.querySelector("body > div.NBxL9e.iWO5td > div > div.I7OXgf.xdwSIe.ZEeHrd.Inn9w.iWO5td > div.OE6hId.J9fJmf > div:nth-child(2) > span > span").click();')
                    continue
                
                self.click('div[role="button"][jsname="X5DuWc"]') #clear form
                self.execute_script('document.querySelector("body > div.NBxL9e.iWO5td > div > div.I7OXgf.xdwSIe.ZEeHrd.Inn9w.iWO5td > div.OE6hId.J9fJmf > div:nth-child(2) > span > span").click();') #click on clear form button
                self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
                logger.info(f'form cleared on exit, on {url}') #DEBUG                                       
        
    def set_folder_name(cleaned_form_title):
        global folder_form_title
        cleaned_form_title = cleaned_form_title.strip() #strip space and tabs
        cleaned_form_title = cleaned_form_title.translate(str.maketrans("ğĞıİüÜşŞöÖçÇ", "gGiIuUsSoOcC")) #special characters to EN chars
        cleaned_form_title = cleaned_form_title.replace(" ", "_") #switch spaces with underscore
        cleaned_form_title = re.sub(r'[^\w\s]', '', cleaned_form_title) #remove special chars
        folder_form_title = f"{form_path}{cleaned_form_title}"
        if os.path.exists(f"{form_path}untitled_folder"): #check TEMP folder exist
            try: os.rename(f"{form_path}untitled_folder", folder_form_title)
            except: pass
        
    def do_parse(self):
        global page_no, form_title, folder_form_title

        self.wait_for_element_visible('[class="HB1eCd-UMrnmb"]') #wait for site load
        self.sleep(3) #IMPROVE6
        
        page_no += 1
        html_content = self.get_page_source() #get html
        page_name = f"page{page_no}.html" #save html
        page_name = str(page_name) #get html page name
        
        if page_no == 1: folder_form_title = None
        try:
            if os.path.exists(folder_form_title):
                page_path_name = os.path.join(folder_form_title, page_name)
        except:
            if not os.path.exists(f"{form_path}untitled_folder"): #check TEMP folder exist
                os.mkdir(f"{form_path}untitled_folder") #create TEMP folder
            page_path_name = os.path.join(f"{form_path}untitled_folder", page_name)
                
        with open(page_path_name,"w", encoding="utf-8") as f: #save page
            f.write(html_content)
        soup = BeautifulSoup(html_content, "html.parser") #set html
        
        description_text,question_list,input_list = [], [] , [] #parsed data lists
        
        #parse form title and set folder name
        meta_element = soup.find("meta", itemprop="name")
        if meta_element:
            form_title = meta_element.get("content")
            if os.path.exists(f"{form_path}untitled_folder"): #check folder
                TestParser.set_folder_name(form_title) #set new folder name
            TestParser.parse_data("form_title",None,form_title,None)
        else: #no form title - set None
            TestParser.set_folder_name(form_title)
            TestParser.parse_data("form_title",None,"None",None)
        
        #parse section title (optional)
        if self.is_element_visible('div[class="Qr7Oae pQK2A"]'): #parse any section title
            element = soup.find("div",class_="SajZGc RVEQke hN5qnf") #CONSTANT class
            try: TestParser.parse_data("section_title",None,element,None)
            except Exception as err:logger.critical(err)
        else: TestParser.parse_data("section_title",None,"None",None) #no section title - set None

        #parse description main/other
        style_str_list = []
        if self.is_element_visible('div[class="cBGGJ OIC90c"]'): #parse main section description
            div_element = soup.find("div", class_="cBGGJ OIC90c") #CONSTANT class
            text_elements = div_element.find_all(string=True, recursive=True) #find all texts
            textnonstyle, style_str_list = [], []
            for element in text_elements:
                text = element.strip()  #remove leading/trailing whitespace
                if text:  #check if text is not empty
                    styles = []
                    parent = element.parent
                    while parent: #check text styles #OPTIMIZE
                        if parent.name == 'a':
                            styles.append(parent.get('href')) #append with link
                            
                        if parent.name == 'ol': #ordered list
                            styles.append('ol')
                        if parent.name == 'ul': #unordered list
                            styles.append('ul')
                            
                        if parent.name in ['b', 'strong']:
                            styles.append('bold')
                        if parent.name in ['i', 'em']:
                            styles.append('latin')
                        if parent.name == 'u':
                            styles.append('underline')
                        parent = parent.parent
                    style_str = ','.join(styles) if styles else 'normal' #no style is normal
                    style_str_list.append(style_str)
                    textnonstyle.append(text)
            for item in textnonstyle: #save description text without style 
                description_text.append(item) 
            TestParser.parse_data("description_text",["text","style"],description_text,style_str_list) #NEW
                
        else: #parse other page section description
            if self.is_element_visible('div[class="vfQisd Q8wTDd OIC90c"]'):
                div_element = soup.find("div", class_="vfQisd Q8wTDd OIC90c") #CONSTANT class
                try: text_elements = div_element.find_all(string=True, recursive=True) #find all texts
                except Exception as err: #THIS MAY CAUSE BUG 
                    text_elements = div_element.find(string=True, recursive=True)
                    logger.critical('216',err)
                textnonstyle,style_str_list = [], []
                for element in text_elements: 
                    text = element.strip()  #remove leading/trailing whitespace
                    if text:  #check if text is not empty
                        styles = []
                        parent = element.parent
                        while parent: #check text styles #OPTIMIZE
                            if parent.name == 'a':
                                styles.append(parent.get('href')) #append with link
                                
                            if parent.name == 'ol': #ordered list
                                styles.append('ol')
                            if parent.name == 'ul': #unordered list
                                styles.append('ul')
                                
                            if parent.name in ['b', 'strong']:
                                styles.append('bold')
                            if parent.name in ['i', 'em']:
                                styles.append('latin')
                            if parent.name == 'u':
                                styles.append('underline')
                            parent = parent.parent
                        style_str = ','.join(styles) if styles else 'normal' #no style is normal
                        style_str_list.append(style_str)
                        textnonstyle.append(text)
                for item in textnonstyle: #save description text without style
                    description_text.append(item) 
            else: #no description found - set None
                description_text.append("None")
                style_str_list.append("None")
            TestParser.parse_data("description_text",["text","style"],description_text,style_str_list)
        
        #parse form div
        form_div = soup.find("form")
        #parse question div
        question_div = form_div.find_all("div", jsmodel="CP1oW") #div with any input
        text_inputs = self.find_elements('input[type="text"]') #BUG
        exception_input = soup.find("div",class_="geS5n AgroKb oQYVNd") #TODO-TEST 
        if exception_input: question_div.insert(0,exception_input)

        #parse required question texts and input types 
        for element in question_div:
            try: #question text and link check in question text
                question_text = element.find("span",class_="M7eMe")
                checklink = question_text.find("a")
            except: pass
            try: #check MC CB
                multiple_choice = element.find("div",jscontroller="UmOCme")
                checkbox = element.find("div",jscontroller="sW52Ae")
            except: pass
            
            text_attr_list = []
            warning_text_list = [] #BUG
            if element.find("span",class_="vnumgf"): #REQUIRED
                question_text = question_text.text #get question text
                if checklink: question_list.append(question_text+checklink["href"]+"*****") 
                else: question_list.append(question_text+"*****")
                question_description_list = []
                try: #get question description
                    q_description = element.find("div",class_="gubaDc OIC90c RjsPE")
                    question_description = q_description.find_all(string=True, recursive=True) #find all texts
                    if question_description[0] is not None:
                        textnonstyle,style_str_list = [],[]
                        for e in question_description: 
                            text = e.strip()  #remove leading/trailing whitespace
                            if text:  #check if text is not empty
                                styles = []
                                parent = e.parent
                                while parent: #check text styles #OPTIMIZE
                                    if parent.name == 'a':
                                        styles.append(parent.get('href')) #append with link
                                    if parent.name == 'ol': #ordered list
                                        styles.append('ol')
                                    if parent.name == 'ul': #unordered list
                                        styles.append('ul')
                                    if parent.name in ['b', 'strong']:
                                        styles.append('bold')
                                    if parent.name in ['i', 'em']:
                                        styles.append('latin')
                                    if parent.name == 'u':
                                        styles.append('underline')
                                    parent = parent.parent
                                style_str = ','.join(styles) if styles else 'normal'
                                style_str_list.append(style_str)
                                textnonstyle.append(text)
                        question_list.append(textnonstyle)
                        question_list.append(style_str_list)
                except:
                    pass
                #check types
                time = element.find("div",class_="IDmXx")
                if element.find("input", type="text") and not time and not multiple_choice and not checkbox: #text
                    text_attr_list.append("text*****")
                    try:
                        attribute = element.find("input", class_="whsOnd zHQkBf")
                        if attribute:    
                            attribute_value_min = attribute.get("min")#smaller/smaller equal
                            attribute_value_max = attribute.get("max")#bigger/bigger equal
                            
                            if attribute_value_max and attribute_value_min: #between
                                attribute_value = f"{attribute_value_min}-{attribute_value_max}"
                            elif attribute_value_min: #min
                                attribute_value = f">{attribute_value_min}"
                            elif attribute_value_max: #max
                                attribute_value = f"{attribute_value_max}<"
                            else:
                                attribute_value = "None"
                            text_attr_list.insert(1,attribute_value)
                    except:
                        attribute_value = "None"
                        text_attr_list.insert(1,attribute_value)
                    input_list.append(text_attr_list)
                elif element.find("input",type="email"):
                    temp_list = ["email*****"]
                    input_list.append(temp_list)
                elif element.find("input",type="url"):
                    temp_list = ["url*****"]
                    input_list.append(temp_list)
                elif element.find("input", type="date"): #date
                    input_list.append("date*****")
                elif element.find("input",type="text") and time: #time
                    input_list.append("time*****")
                elif element.find("textarea"): #textarea
                    #TODO: add attribute feature
                    input_list.append("textarea*****")                   
                elif element.find("div",jscontroller="UmOCme"): #multiple choice
                    multiple_choice_list = []
                    multiple_choice_options = multiple_choice.find_all("span",class_="aDTYNe snByac OvPDhc OIC90c")
                    if multiple_choice.find("input", type="text"):
                        multiple_choice_list.insert(0,"MCT*****") #multiple choice with text input
                        mc_text = multiple_choice.find("div",class_="nWQGrd zwllIb zfdaxb")
                        multiple_choice_options.append(mc_text)
                    else: multiple_choice_list.insert(0,"MC*****")
                    for mc in multiple_choice_options:
                        mc = mc.text
                        multiple_choice_list.append(mc)
                    input_list.append(multiple_choice_list)   
                elif element.find("div",jscontroller="sW52Ae"): #checkbox
                    checkbox_list = []
                    checkbox_options = checkbox.find_all("span",class_="aDTYNe snByac n5vBHf OIC90c")
                    if checkbox.find("input",type="text"):
                        checkbox_list.insert(0,"CBT*****") #checkbox with text input
                        cb_text = checkbox.find("div",class_="eBFwI RVLOe")
                        checkbox_options.append(cb_text)
                    else:
                        checkbox_list.insert(0,"CB*****")
                    for cb in checkbox_options:
                        cb = cb.text
                        checkbox_list.append(cb)
                    input_list.append(checkbox_list)                               
                elif element.find("div",role="listbox"):  #dropdown
                    dropdown = element.find("div",role="listbox")
                    dropdown_list = []
                    dropdown_options = dropdown.find_all("span",class_="vRMGwf oJeWuf")
                    for do in dropdown_options:
                        do = do.text
                        dropdown_list.append(do)
                    dropdown_list.insert(0,"DD*****")
                    input_list.append(dropdown_list)                   
                elif element.find("span",class_="l4V7wb Fxmcue cd29Sd"): #upload
                    input_list.append("upload")                    
                elif element.find("div",jscontroller="FYWcYb"): #linear scale
                    linear_scale = element.find("div",jscontroller="FYWcYb")
                    linear_scale_list = []
                    linear_scale_options = linear_scale.find_all("label",class_="T5pZmf")
                    for ls in linear_scale_options:
                        ls_option = ls.find("div",class_="Zki2Ve")
                        if ls_option:
                            ls_option = ls_option.text
                            linear_scale_list.append(ls_option)
                    linear_scale_list.insert(0,"ls*****")
                    input_list.append(linear_scale_list)                  
                elif element.find("div",class_="gTGYUd"): #any multiple grid
                    anygrid = element.find("div",class_="gTGYUd")
                    if anygrid.find("div",role="radiogroup"): #multiple choice grid
                        column_list = []
                        columngrid = anygrid.find("div",class_="ssX1Bd KZt9Tc") 
                        columns = columngrid.find_all("div",class_="V4d7Ke OIC90c")
                        for column in columns: #get column titles
                            column_list.append(column.text)
                        column_list.insert(0,"MCGcol*****")
                        
                        row_list = [] 
                        rows = anygrid.find_all("div",class_="lLfZXe fnxRtf EzyPc")
                        for row in rows: #get row titles
                            row_list.append(row.text)
                        row_list.insert(0,"MCGrow*****")
                        
                        col_row_list = []
                        for i in column_list:
                            col_row_list.append(i)
                        for i in row_list:
                            col_row_list.append(i)
                            
                        input_list.append(col_row_list) #improve
                        
                    else: #checkbox grid
                        column_list = []
                        columngrid = anygrid.find("div",class_="ssX1Bd KZt9Tc") 
                        columns = columngrid.find_all("div",class_="V4d7Ke OIC90c")
                        for column in columns: #get column titles
                            column_list.append(column.text)
                        column_list.insert(0,"CBGcol*****")
                            
                        row_list = []
                        gridtable = element.find("div",class_="ufh7vf")
                        gridtable.find("div",class_="ssX1Bd")
                        rows = gridtable.find_all("div",class_="V4d7Ke wzWPxe OIC90c")
                        for row in rows:
                            row_list.append(row.text)
                        row_list.insert(0,"CBGrow*****")
                        
                        col_row_list = []
                        for i in column_list:
                            col_row_list.append(i)
                        for i in row_list:
                            col_row_list.append(i)
                            
                        input_list.append(col_row_list) #IMPROVE
                else:
                    input_list.append("not_assigned*****")
            
            else: #OPTIONAL
                question_text = question_text.text #get question text
                if checklink:
                    question_list.append(question_text+checklink["href"]) 
                else:
                    question_list.append(question_text)
                question_description_list = []
                try: #get question description
                    q_description = element.find("div",class_="gubaDc OIC90c RjsPE")
                    question_description = q_description.find_all(string=True, recursive=True)
                    if question_description[0] is not None:
                        textnonstyle = []
                        style_str_list = []
                        for e in question_description:
                            text = e.strip()  #remove leading/trailing whitespace
                            if text:  #check if text is not empty
                                styles = []
                                parent = e.parent
                                while parent: #check text styles #OPTIMIZE
                                    if parent.name == 'a':
                                        styles.append(parent.get('href')) #append with link
                                    if parent.name == 'ol': #ordered list
                                        styles.append('ol')
                                    if parent.name == 'ul': #unordered list
                                        styles.append('ul')
                                    if parent.name in ['b', 'strong']:
                                        styles.append('bold')
                                    if parent.name in ['i', 'em']:
                                        styles.append('latin')
                                    if parent.name == 'u':
                                        styles.append('underline')
                                    parent = parent.parent
                                style_str = ','.join(styles) if styles else 'normal'
                                style_str_list.append(style_str)
                                textnonstyle.append(text)
                        question_list.append(textnonstyle)
                        question_list.append(style_str_list)
                except: pass
                #check types
                time = element.find("div",class_="IDmXx")
                if element.find("input", type="text") and not time and not multiple_choice and not checkbox: #text
                    text_attr_list = []
                    text_attr_list.append("text")
                    try:
                        attribute = element.find("input", class_="whsOnd zHQkBf")
                        if attribute:
                            attribute_value_min = attribute.get("min")#smaller/smaller equal
                            attribute_value_max = attribute.get("max")#bigger/bigger equal
                            if attribute_value_max and attribute_value_min: #between
                                attribute_value = f"{attribute_value_min}-{attribute_value_max}"
                            elif attribute_value_min: #min
                                attribute_value = f">{attribute_value_min}"
                            elif attribute_value_max: #max
                                attribute_value = f"{attribute_value_max}<"
                            else:
                                attribute_value = "None"
                            text_attr_list.insert(1,attribute_value)
                    except:
                        attribute_value = "None"
                        text_attr_list.insert(1,attribute_value)
                    input_list.append(text_attr_list)
                elif element.find("input",type="email"):
                    temp_list = ["email"]
                    input_list.append(temp_list)
                elif element.find("input",type="url"):
                    temp_list = ["url"]
                    input_list.append(temp_list)
                elif element.find("input", type="date"): #date
                    input_list.append("date")
                elif element.find("input",type="text") and time: #time
                    input_list.append("time")
                elif element.find("textarea"): #textarea
                    #improve-attribute feature
                    input_list.append("textarea")                   
                elif element.find("div",jscontroller="UmOCme"): #multiple choice
                    multiple_choice_list = []
                    multiple_choice_options = multiple_choice.find_all("span",class_="aDTYNe snByac OvPDhc OIC90c")
                    if multiple_choice.find("input", type="text"):
                        multiple_choice_list.insert(0,"MCT") #multiple choice with text input
                        mc_text = multiple_choice.find("div",class_="nWQGrd zwllIb zfdaxb")
                        multiple_choice_options.append(mc_text)
                    else:
                        multiple_choice_list.insert(0,"MC")
                    for mc in multiple_choice_options:
                        mc = mc.text
                        multiple_choice_list.append(mc)
                    input_list.append(multiple_choice_list)   
                elif element.find("div",jscontroller="sW52Ae"): #checkbox
                    checkbox_list = []
                    checkbox_options = checkbox.find_all("span",class_="aDTYNe snByac n5vBHf OIC90c")
                    
                    if checkbox.find("input",type="text"):
                        checkbox_list.insert(0,"CBT") #checkbox with text input
                        cb_text = checkbox.find("div",class_="eBFwI RVLOe")
                        checkbox_options.append(cb_text)
                    else:
                        checkbox_list.insert(0,"CB")
                    for cb in checkbox_options:
                        cb = cb.text
                        checkbox_list.append(cb)
                    input_list.append(checkbox_list)                               
                elif element.find("div",role="listbox"):  #dropdown
                    dropdown = element.find("div",role="listbox")
                    dropdown_list = []
                    dropdown_options = dropdown.find_all("span",class_="vRMGwf oJeWuf")
                    for do in dropdown_options:
                        do = do.text
                        dropdown_list.append(do)
                    dropdown_list.insert(0,"DD")
                    input_list.append(dropdown_list)                   
                elif element.find("span",class_="l4V7wb Fxmcue cd29Sd"): #upload
                    input_list.append("upload")                    
                elif element.find("div",jscontroller="FYWcYb"): #linear scale
                    linear_scale = element.find("div",jscontroller="FYWcYb")
                    linear_scale_list = []
                    linear_scale_options = linear_scale.find_all("label",class_="T5pZmf")
                    for ls in linear_scale_options:
                        ls_option = ls.find("div",class_="Zki2Ve")
                        if ls_option:
                            ls_option = ls_option.text
                            linear_scale_list.append(ls_option)
                    linear_scale_list.insert(0,"ls")
                    input_list.append(linear_scale_list)                  
                elif element.find("div",class_="gTGYUd"): #any multiple grid
                    anygrid = element.find("div",class_="gTGYUd")
                    if anygrid.find("div",role="radiogroup"): #multiple choice grid
                        column_list = []
                        columngrid = anygrid.find("div",class_="ssX1Bd KZt9Tc") 
                        columns = columngrid.find_all("div",class_="V4d7Ke OIC90c")
                        for column in columns: #get column titles
                            column_list.append(column.text)
                        column_list.insert(0,"MCGcol")
                        
                        row_list = [] 
                        rows = anygrid.find_all("div",class_="lLfZXe fnxRtf EzyPc")
                        for row in rows: #get row titles
                            row_list.append(row.text)
                        row_list.insert(0,"MCGrow")
                        
                        col_row_list = []
                        for i in column_list:
                            col_row_list.append(i)
                        for i in row_list:
                            col_row_list.append(i)
                            
                        input_list.append(col_row_list) #improve
                        
                    else: #checkbox grid
                        column_list = []
                        columngrid = anygrid.find("div",class_="ssX1Bd KZt9Tc") 
                        columns = columngrid.find_all("div",class_="V4d7Ke OIC90c")
                        for column in columns: #get column titles
                            column_list.append(column.text)
                        column_list.insert(0,"CBGcol")
                            
                        row_list = []
                        gridtable = element.find("div",class_="ufh7vf")
                        gridtable.find("div",class_="ssX1Bd")
                        rows = gridtable.find_all("div",class_="V4d7Ke wzWPxe OIC90c")
                        for row in rows:
                            row_list.append(row.text)
                        row_list.insert(0,"CBGrow")
                        
                        col_row_list = []
                        for i in column_list:
                            col_row_list.append(i)
                        for i in row_list:
                            col_row_list.append(i)
                            
                        input_list.append(col_row_list) #improve
                else: input_list.append("not_assigned")
            
            TestParser.parse_data("questions","question_description",question_list,question_description_list)
            TestParser.parse_data("input_types",None,input_list,None)
        
    def parse_data(jsontitle, subtitle, element1, element2):
        global page_no, form_title, folder_form_title
        
        filename = f"parsed_{page_no}.json"
        json_path_name = os.path.join(folder_form_title, filename)
        
        if not isinstance(element1, str) and not isinstance(element1, list):
            try: element1 = element1.text
            except Exception as err: logger.critical('622 ',err)
        try:
            with open(json_path_name, "r", encoding="utf-8") as f:
                jsondata = json.load(f)
        except FileNotFoundError: jsondata = {}
            
        if subtitle and element2: 
            jsondata[jsontitle] = {subtitle[0]: element1,subtitle[1]: element2}
        elif subtitle and not element2:
            jsondata[jsontitle] = {subtitle[0]: element1}
        else: jsondata[jsontitle] = element1
        
        with open(json_path_name, "w", encoding="utf-8") as f:
            json.dump(jsondata, f, indent=4, ensure_ascii=False)
    
    def fill_form(self):
        global page_no, form_title, folder_form_title
        filename = f"parsed_{page_no}.json"
        json_path_name = os.path.join(folder_form_title, filename)
        with open(json_path_name, "r",encoding="utf-8") as file:
            json_data = json.load(file)

        i,ilist,w_list,warning_list = -1, [], [], []
        
        for input_t in json_data.get("input_types", []):
            if isinstance(input_t,list):
                if "MC" in ilist:
                    if "ls" in input_t[0] or "MCGcol" in input_t[0] or "MCT" in input_t[0] or "MC" in input_t[0]:
                        continue
                if "CB" in ilist:
                    if "CBGcol" in input_t[0] or "CBT" in input_t[0] or "CB" in input_t[0]:
                        continue
                if input_t[0] == "text*****" or input_t[0] == "text":
                    w_list.append(input_t)
                if input_t[0] not in ilist:
                    ilist.append(input_t[0])
            else:
                if input_t not in ilist:
                    if input_t != "MCT" or input_t != "CBT":
                        ilist.append(input_t)
                    
        for z, input_type in enumerate(ilist):
            if "text*****" == ilist[z]:
                #statements
                inputs = self.find_elements('input[type="text"]')
                for i,input in enumerate(inputs):
                    try:
                        filled = input.get_attribute('value') #has any value
                        if not filled: #no value
                            try:
                                text = f"ipsumlorem{i}" #set try text
                                input.send_keys(text) #input try text
                                self.click('div[class="T2dutf"]') #for error check
                                if self.is_element_visible('span[class="RHiWt"]'): #check any error
                                    warning_text = self.find_element('span[class="RHiWt"]') #find warning text
                                    json_data["input_types"][i].append(warning_text.text)
                                    updated_json = json.dumps(json_data, indent=4)
                                    with open(json_path_name, 'w', encoding="utf-8") as f:
                                        f.write(updated_json)
                                    css_selector = f'input.whsOnd.zHQkBf[jsname="YPqjbf"][data-initial-value={text}]' #select last entered example
                                    input_element = self.find_element(By.CSS_SELECTOR, css_selector) #find
                                    actions = ActionChains(self.driver)
                                    actions.double_click(input_element).perform() #double click example text
                                    input.send_keys(Keys.BACKSPACE) #delete example text
                                    self.click('div[class="T2dutf"]') #for error check
                                    if self.is_element_visible('span[class="RHiWt"]'): #check any error 
                                        if w_list[i][0] == "text*****":
                                            if ">" in w_list[i][1]: #bigger
                                                number = w_list[i][1][1:] #get number
                                                text = int(number)+1 #set text
                                            elif "<" in w_list[i][1]: #smaller
                                                number = w_list[i][1][:1] #get number
                                                text = int(number)-1 #set text
                                            elif "-" in w_list[i][1]: #between
                                                parts = w_list[i][1].split("-")
                                                number = parts[0]  #min number
                                                number = int(number) #convert
                                                text = number+1 #+1
                                            #improve: equal, figure only, integer, contain, max char, min char, match, not between, not equal
                                            else:    
                                                text = f"loremipsum{i}" #set text
                                            input.send_keys(text) #input example text
                                            self.click('div[class="T2dutf"]') #for error check
                                        if self.is_element_visible('span[class="RHiWt"]'): #check any error
                                            css_selector = f'input.whsOnd.zHQkBf[jsname="YPqjbf"][data-initial-value={text}]' #select last entered example
                                            input_element = self.find_element(By.CSS_SELECTOR, css_selector) #find
                                            actions = ActionChains(self.driver)
                                            actions.double_click(input_element).perform() #double click example text
                                            input.send_keys(Keys.BACKSPACE) #delete example text
                            except Exception as err: pass
                    except Exception as err: logger.critical(f'712 {err}')
                    else: continue
            elif "email*****" == ilist[z]:
                inputs = self.find_elements('input[type="email"]')
                for input in inputs:
                    filled = input.get_attribute('value')
                    if not filled:
                        text = f"ipsumlorem" #set try text
                        input.send_keys(text) #input try text
                        self.click('div[class="T2dutf"]') #for error check
                        if self.is_element_visible('span[class="RHiWt"]'): #check any error
                            warning_text = self.find_element('span[class="RHiWt"]') #find warning text
                            for item in json_data["input_types"]:
                                if "email" in item or "email*****" in item:
                                    item.append(warning_text.text)
                                    break
                            updated_json = json.dumps(json_data, indent=4)
                            with open(json_path_name, 'w', encoding="utf-8") as f:
                                f.write(updated_json)
                            css_selector = f'input.whsOnd.zHQkBf[jsname="YPqjbf"][data-initial-value={text}]' #select last entered example
                            input_element = self.find_element(By.CSS_SELECTOR, css_selector) #find
                            actions = ActionChains(self.driver)
                            actions.double_click(input_element).perform() #double click example text
                            input.send_keys(Keys.BACKSPACE) #delete example text
                            self.click('div[class="T2dutf"]') #for error check
                            if self.is_element_visible('span[class="RHiWt"]'): #check any error 
                                input.send_keys(user_email)
                    else:
                        break
            elif "url*****" == ilist[z]:
                inputs = self.find_elements('input[type="url"]')
                for input in inputs:
                    filled = input.get_attribute('value')
                    if not filled:
                        text = f"ipsumlorem" #set try text
                        input.send_keys(text) #input try text
                        self.click('div[class="T2dutf"]') #for error check
                        if self.is_element_visible('span[class="RHiWt"]'): #check any error
                            warning_text = self.find_element('span[class="RHiWt"]') #find warning text
                            for item in json_data["input_types"]:
                                if "url" in item or "url*****" in item:
                                    item.append(warning_text.text)
                                    break
                            updated_json = json.dumps(json_data, indent=4)
                            with open(json_path_name, 'w', encoding="utf-8") as f:
                                f.write(updated_json)
                            css_selector = f'input.whsOnd.zHQkBf[jsname="YPqjbf"][data-initial-value={text}]' #select last entered example
                            input_element = self.find_element(By.CSS_SELECTOR, css_selector) #find
                            actions = ActionChains(self.driver)
                            actions.double_click(input_element).perform() #double click example text
                            input.send_keys(Keys.BACKSPACE) #delete example text
                            self.click('div[class="T2dutf"]') #for error check
                            if self.is_element_visible('span[class="RHiWt"]'): #check any error 
                                input.send_keys("https://www.example.com/")
                    else:
                        break
            elif "textarea*****" == ilist[z]:
                inputs = self.find_elements('textarea')
                for i,input in enumerate(inputs):
                    filled = input.get_attribute('value')
                    if not filled:
                        input.send_keys(f"loremipsum{i}")
                    else:
                        break
        
            elif "MC*****" in ilist[z] or "ls*****" == ilist[z] or "MCGcol*****" in ilist[z]:
                inputs = self.find_elements('[role="radio"][aria-posinset="1"]')
                for input in inputs:
                    try:
                        input.click()
                    except:
                        pass
            elif "CB*****" in ilist[z] or "CBGcol*****" in ilist[z]:
                inputs = self.find_visible_elements('[role="checkbox"]')
                #improve: min, max, exact
                for input in inputs:
                    try:
                        filled = input.get_attribute('aria-checked')
                        if filled != 'true':
                            input.click()
                        else:
                            continue
                    except:
                        pass
                    #try:
                        #if input.is_selected():
                            #pass
                        #else:
                            #input.click()
                    #except:
                        #pass
            elif "DD*****" == ilist[z]:
                dds = self.find_elements("[jsname='d9BH4c']")
                c = 0
                for dd in dds:
                        dd.click() #open dropdown options
                        self.sleep(2)
                        dd_options = self.find_visible_elements('[role="option"]') #get dropdown options
                        dd_options[c].click()
                        self.sleep(2)
                        self.click('div[class="T2dutf"]') #for error check
                        while True:
                            if self.is_element_visible('span[class="RHiWt"]'):
                                c+=2
                                dd.click() #open dropdown options
                                self.sleep(2)
                                dd_options = self.find_visible_elements('[role="option"]') #take options
                                dd_options[c].click()
                                self.sleep(2)
                                self.click('div[class="T2dutf"]') #for error check
                            else:
                                break
                            
            elif "date*****" == ilist[z]:
                inputs = self.find_elements('input[type="date"]')
                for input in inputs:
                    filled = input.get_attribute('value')
                    if not filled: input.send_keys("1990-01-01")
                    else: break
            elif "time*****" == ilist[z]:
                filled = input.get_attribute('value')
                if not filled:
                    self.type('[aria-label="Hour"]',12)
                    self.type('[aria-label="Minute"]',12)
                else: break
            
            elif "upload*****" == ilist[z]: pass #TODO: 

if __name__ == "__main__":
    TestParser.ParserLauncher(TestParser,False)

![parser_logo](https://github.com/corazonthedev/Google-form-parser/assets/137296314/3573a403-0aa4-46f1-9fc3-bbdaf7601e94)

# Overview

This is a python code for parsing Google forms into JSON files.

This parser is not a finished project, there may be unseen bugs or errors. You can contribute as you like.

# Requirements
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  
- [SeleniumBase](https://seleniumbase.io/)


# Installation and Launching
1. Clone the repository:
   ```console
   git clone https://github.com/corazonthedev/Google-form-parser.git
   cd Google-form-parser
   pip install -r requirements.txt
   python google_form_parser.py
   ```

2. Launch directly using cmd:
    ```console
    python google_form_parser.py
    ```
# How to use
  1.
  ![1](https://github.com/corazonthedev/Google-form-parser/assets/137296314/dac9885a-34a3-4470-baf6-38fa36ddf819)

  
  - Enter your gmail
  - Enter your password
  - Enter form link
  - Submit

**Note**: Parser is currently unable to tell is your link/email/password valid or not. So be sure about your inputs or it will not work.


Parser will automatically parse the form 
![2](https://github.com/corazonthedev/Google-form-parser/assets/137296314/1bdea6a0-bac0-47f8-a6d4-eb56b3144e14)


and exit
![3](https://github.com/corazonthedev/Google-form-parser/assets/137296314/803536f8-3bde-46c7-9bc2-9eb5f342bd64)


For more you can always check the latest.log which will be created after your first launch

![4](https://github.com/corazonthedev/Google-form-parser/assets/137296314/047851ff-95db-4ca0-b168-1bb6a80f8ec9)
![5](https://github.com/corazonthedev/Google-form-parser/assets/137296314/c345e1b2-d528-45b9-8b50-ea8790db3bfe)


  2.
  parsed JSON files and their source are located in FORMS folder with their form title

  ![6](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4841f556-57f0-4844-9f2e-eab9408f8f95)
  ![7](https://github.com/corazonthedev/Google-form-parser/assets/137296314/77915cd1-772a-4e8a-8a96-6b1fbb223f4c)

  
  ![8](https://github.com/corazonthedev/Google-form-parser/assets/137296314/97e16317-3c2b-4fb6-8847-680bc674c278)


  **Note**: There is a loop in parser in order to parse multiple forms at once but after a couple of forms it`s bugging and not parsing, it will be fixed in future.

# How does it work 

At first page there are 2 types of forms

1. No question, Only description


![10](https://github.com/corazonthedev/Google-form-parser/assets/137296314/caff2b87-4264-475e-87c3-d29616f997b3)

2. Questions with description


![11](https://github.com/corazonthedev/Google-form-parser/assets/137296314/9e4e752f-2501-432a-af58-57ff75dbd712)

If there are no visible questions on first page, parser will just parse the description and next.

Otherwise parser will try to fill every question and parse it. 

**Note**: Parser will try to fill every question because it will also parse the Answer Verifications. 
![12](https://github.com/corazonthedev/Google-form-parser/assets/137296314/5f26dd3a-4451-43b9-a4ab-1f57ee4e3549)

When parser finishes filling out questions on current page, it will next and loop untill the last page. 

**Note**: Currently some forms are unparsable because of Google form's html-js structure. **If your form is unparsable it will say UNPRASABLE on latest.log**.

# Visualisation
For visualisation in __line 81__ set headless=False, so you can see the parsing process. 
![9](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4ff49529-5928-4609-a1ad-d3b926dfabae)

Clicking anywhere on browser while running with headless=False may occure problems.

## How to read JSON


## Disclaimer:

### Why do I have to log-in ?
  You have to log-in your Google account because you can access Google forms **only if you loged-in** (there are some public forms which you can access without logging-in but not most of them)

__THIS PARSER DOES NOT SAVE OR KEEP YOUR EMAIL OR PASSWORD.__

Although it only works with your manuel input I **highly recommend not to use your main account.**

I tried different ways to access Google forms but wihout logging-in you can't view all form pages. If you do have an idea you can contribute to this parser.





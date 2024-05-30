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


  **Note**: There is a loop in parser and link.txt file in order to parse multiple forms at once but after a couple of forms it`s bugging and not parsing, it will be fixed in future.


  example forms you can use:

  [Try with everything](https://docs.google.com/forms/d/e/1FAIpQLSdWX-2aT1Wdu1g5W9wN7OlbQk877O2_JY6F10vJSpzOtjhFGw/viewform?fbzx=-3044991410149344237)


  [form with sections](https://docs.google.com/forms/d/e/1FAIpQLScbErtBFKDahcdqYAENV6SsvwJrM2iQYv-cfRpwEdmmChQgIg/viewform)


  [internship application](https://docs.google.com/forms/d/e/1FAIpQLSczsQCWixSIY2kffUxlN2JwVe09H-dlxJucG60QWiD8USsEZw/viewform)

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
For visualisation in __line 82__ set headless=False, so you can see the parsing process. 
![9](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4ff49529-5928-4609-a1ad-d3b926dfabae)

Clicking anywhere on browser while running with headless=False may occure problems.

## How to read JSON

[debug form](https://docs.google.com/forms/d/e/1FAIpQLSdWX-2aT1Wdu1g5W9wN7OlbQk877O2_JY6F10vJSpzOtjhFGw/viewform?fbzx=-3044991410149344237) 

Parser firstly save form title, section title (if available) and description text. Description text will be divided into text and style. In text you can see each line of text 
with different styles. In styles you can see which line has which styles. 

**Note**: This can also be done with saving each line with their style.

### First section:


![1](https://github.com/corazonthedev/Google-form-parser/assets/137296314/14f34e4e-0a64-4594-9d9d-200b3ab9587d)
![2](https://github.com/corazonthedev/Google-form-parser/assets/137296314/685ed844-7c85-4bb8-85e3-e88e2b84642e)


### Second Section:


![3](https://github.com/corazonthedev/Google-form-parser/assets/137296314/46ea8ab7-ce27-4f54-9de3-f2b75ab2f500)
![4](https://github.com/corazonthedev/Google-form-parser/assets/137296314/554a1844-970c-4da9-b53d-eada53c9d5b7)

Parser will save every question's text. And if a question is mandatory it will add ***** at the end of question text (can be improved)

If question has a description 

![a](https://github.com/corazonthedev/Google-form-parser/assets/137296314/e007569d-4a87-407f-a064-990b8672c07f)

Parser will save it in questions same as section description, with text and styles

![6](https://github.com/corazonthedev/Google-form-parser/assets/137296314/bfed17c9-d989-476e-b707-5bf726413a00)


**Note**: Parser is currently unable to save question texts with styles, for example: if a link is present in question text parser will not save it properly.

![9](https://github.com/corazonthedev/Google-form-parser/assets/137296314/8fbdab54-4996-4db8-bc31-4aa07b28d2e4)
![10](https://github.com/corazonthedev/Google-form-parser/assets/137296314/e8e4edd2-77c6-45a6-8429-e68731553f76)

Unfortunately parser is unable to parse some text question's answer verifications. 

If your form is unparsable you can see it on latest.log

![11](https://github.com/corazonthedev/Google-form-parser/assets/137296314/5f2ee44f-9a99-4636-8d1a-18afae35af4a)

Also you can see the parser's last point with image

![12](https://github.com/corazonthedev/Google-form-parser/assets/137296314/76644ae7-849d-446a-b379-1ec80cea5f04)

For inputs:

![8](https://github.com/corazonthedev/Google-form-parser/assets/137296314/e115e55f-594e-4a97-8a1b-cef8206c435b)

text is for text inputs. text questions are saved witn answer verification, if question has no answer verification it will save as "None"

![13](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4a50bd4a-c530-4ead-8fd1-7c1401d8c3e5)
![14](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4fb02498-90dd-487a-95ac-1dc101713643)

textarea is for text area inputs. 

![15](https://github.com/corazonthedev/Google-form-parser/assets/137296314/c1c7b9bb-aaf5-49cf-a496-0c4cbd88497a)
![16](https://github.com/corazonthedev/Google-form-parser/assets/137296314/52246b21-c3a1-4b27-9264-7b3298c05343)


### Third Section:

if a multiple choice question has description text it will save with it's description
same in checkbox 


![17](https://github.com/corazonthedev/Google-form-parser/assets/137296314/e3a03487-d73f-48a7-b8d0-651131c9a7b2)
![18](https://github.com/corazonthedev/Google-form-parser/assets/137296314/5157e17c-ec79-4b1c-8eea-f9885e2af504)


For inputs:

MC is for multiple choice and MCT is for multiple choice with "other" option.
CB is for checkbox and CBT is for checkbox with "other" option.

![19](https://github.com/corazonthedev/Google-form-parser/assets/137296314/b2ccaee2-ab87-4a2c-a9e4-bd7ca3e99cdc)

DD is for dropdown.

![20](https://github.com/corazonthedev/Google-form-parser/assets/137296314/90b941ba-fe70-41ce-a026-4128314f07f3)
![21](https://github.com/corazonthedev/Google-form-parser/assets/137296314/305be39e-cfa8-4666-be20-41f0e91f9135)
![22](https://github.com/corazonthedev/Google-form-parser/assets/137296314/b312357d-6ff8-42ec-b66d-8469b1f2e0c8)



### Fourth Section:


![23](https://github.com/corazonthedev/Google-form-parser/assets/137296314/b5f18545-0d02-4a55-87b7-768892a678ac)


![24](https://github.com/corazonthedev/Google-form-parser/assets/137296314/4f80955d-d7fa-4a41-a7a3-cda810b68dd8)


![25](https://github.com/corazonthedev/Google-form-parser/assets/137296314/47d2f00c-a31f-48fd-b662-76c2760de986)

LS is for linear scale. MCG is for Multiple Choice Grid. CBG is for CheckBox Grid.


### Fifth section:

![26](https://github.com/corazonthedev/Google-form-parser/assets/137296314/45970db1-2d57-4bd4-bd0e-a592fd9d7169)

![27](https://github.com/corazonthedev/Google-form-parser/assets/137296314/df2be21a-4187-457a-a917-81afc589134a)


Parser in unable to upload at this point.

## Disclaimer:

### Why do I have to log-in ?
  You have to log-in your Google account because you can access Google forms **only if you loged-in** (there are some public forms which you can access without logging-in but not most of them)

__THIS PARSER DOES NOT SAVE OR KEEP YOUR EMAIL OR PASSWORD.__

Although it only works with your manuel input I **highly recommend not to use your main account.**

I tried different ways to access Google forms but wihout logging-in you can't view all form pages. If you do have an idea you can contribute to this parser.





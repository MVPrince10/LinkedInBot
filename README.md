**Set Up**

1. install python
2. set up and active python virtual env
3. install pip
4. > pip install -r requirements.txt
   > python main.py
   > export LNK_PWD=<your linkedIn password>
   > update username variable in main.py

**Higher level description:**

This is a semi-automated-bot.  (user confirmation before message send) 
This bot operates in the following way:
1. executes scrape_companies(): this method searches a search term and selects the company results.
   - searches only US companies
   - can be narrowed by 3 company sizes SML (1-10), MED(11-50), LRG(>50)
   - MAX_PAGE = number of pages to scrape per search term.
2. executes scrape_people():
   - finds all people in each company
   - writes results to people.csv ("company_link", "person_link")
   - can be narrowed to specific job titles
3. execute message_people():
   - utilizes pre-drafted message
   - semi-automated because this bot will require user action to click "connect" -> "add note" -> "send"
   - WAIT_TIME = how long to wait for you to click "Send", if you don't click within this time is seconds, skips user
   - saves users that have been sent a message in sent.csv ("send", "person_link")
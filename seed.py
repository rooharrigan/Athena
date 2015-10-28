from model import connect_to_db, db, Country, User


##############################################################################
# Seed the database with country information

def load_countries():
    """Loads countries and country information into posgreSQL Athena database"""
    pass

def get_country_infobox():
    """ API call to wikipedia to grab the string of JSON for the requested country
    and return a dictionary that begins at the template/key 'Infobox country'

    """ 
    #Get country from the form and check that it's a country, and uppercase the first letter:
    country = request.args.get("country")
    country = country.title()


    #Define query params
    query_params = {
    "action": "query",
    "titles": country,
    "prop": "revisions",
    "rvprop": "content",
    "format": "json",
    "formatverson": 2
    }

    #Query the wikipedia API for the JSON object, convert to Python dictionary
    r = requests.get("https://en.wikipedia.org/w/api.php?", params=query_params)
    info = r.json()

    #Key into the dictionary to the Infobox level
    infobox_json = str(info["query"]["pages"].values()[0]["revisions"][0])

    #Parse the dictionary and filter it by wiki template names
    wikicode = mwparserfromhell.parse(infobox_json)
    templates = wikicode.filter_templates()

    #Find the template with the string "infobox" in the name and return new dictionary
    #starting at the Infobox level, parsed again
    j = 0
    for i in templates:
        country_dict = templates[j]
        template = country_dict.name
        template = template.strip()
        if template.find("Infobox") != -1:
            print "Got the infobox!\n"
            template_list = mwparserfromhell.parse(country_dict).filter_templates()
            infobox_template = template_list[0]
            capital = get_capital(infobox_template, country)
            return render_template("quiz_questions.html", country=country)
        else:
            print "No infobox yet."
        j += 1


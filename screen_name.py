from twython import Twython


# Paste your codes here
app_key = 'o2364QzhfTxjCCwZ6guKTPN4i'
app_secret ='JGwxQzbtLGsIu2HXV4f2T1GALgKrNm7O7wdZs6xBzoMZVnWksZ'
oauth_token = '3568557440-z3V9Ki4eptgt09nAnUhCPtF8eYy3btN2jR9QNBM'
oauth_token_secret= 'qPR9BlhPcLxvnRO6AETMoBo0eZaF1DP0CF4fYbUqaN9E7'

# Create twitter thing to query
#
twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)



# What to look up (Twitter id:s)
ids = ["megha4467","shalanwalunj","Sujata4424","megha4467"]

# Create a comma separated string from the previous list
comma_separated_string = ",".join(ids)


# Query twitter with the comma separated list
output = twitter.lookup_user(screen_name=comma_separated_string)

username_list=[]

# Loop through the results (Twitter screen names)
for user in output:
    print user["id_str"]



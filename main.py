import nozbe


username = input("Username:")
password = input("Pass:")
n = nozbe.Nozbe()
n.login(username, password)
#COMMENT 1
print("Hello, World")
#COMMENT 2
'''Long COMMENT Type 1'''
print("Thanadon")
"""Long COMMENT Type 2"""
x = 10
y = 50
z = 100
if x <= y and y <= z:
  # do something
  print("Bad")

if x <= y <= z:
  print("Good")
  # do something

# Use the ‘in’ keyword

# Bad
city = 'Nairobi'
found = False
if city == 'Nairobi' or city == 'Kampala' or city == 'Lagos':
  found = True

# Good
city = 'Nairobi'
found = city in {'Nairobi', 'Kampala', 'Lagos'}
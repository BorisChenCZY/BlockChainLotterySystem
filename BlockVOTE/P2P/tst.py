import re
b = "<sss><sdddd>fjso"
print(re.findall(r'[^<>]+',b))
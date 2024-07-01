# This is where the magic happens! 
import time

print("Hello World!")

try:
    for i in range(10):
        print(f"Code Starting in {10-i} seconds") 
        time.sleep(1)
    
    import main

except Exception as e:
    print(e)

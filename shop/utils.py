import time
import random

def generate_reference():
  base = int(time.time() * 100)

  extra = random.randint(10, 99)

  return str(base + extra)[-11:]
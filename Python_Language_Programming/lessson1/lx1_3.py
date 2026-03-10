import turtle
import random

def randstar():
    turtle.screensize(600,400)
    n = random.randint(5,20)

    for i in range(1,n):
        turtle.up()
        turtle.goto(random.randint(-300,300),random.randint(-200,200))
        turtle.down()
        turtle.pencolor(random.random(),random.random(),random.random())
        turtle.pensize(random.randint(1,10))
        angle = random.randint(5,15)
        step = random.randint(50,150)
        for j in range(1,angle):
            turtle.forward(step)
            turtle.left(360/angle)
            turtle.backward(step)

if __name__ == '__main__':
    random.seed(a=None)
    randstar()
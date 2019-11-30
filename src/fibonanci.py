def main():
    m = 0
    n = 1
    i = 0
    temp = 0
    state = 0
    boo = False

    input = 102
    while(i <= input):
        if(input == 0):
            boo = True
            break
        elif(i == 0):
            i = m + n
            temp = i
        else:
            temp = i
            i = state + i
            if(i == input):
                boo = True
                break
            state = temp
        print(i)
    if(boo):
        print(str(input) + " is fibonanci number.")
    else:
        print(str(input) + " is not fibonanci number.")
        

main()

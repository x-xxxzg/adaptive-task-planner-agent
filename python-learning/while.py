print("我是一个求平均值的计算器。")
user_input = input("请输入数字，完成数字输入后，输入q结束程序：")
sum = 0
count = 0
while user_input != "q":
    nums = float(user_input)
    sum += nums 
    count += 1
    user_input = input("请输入数字，完成数字输入后，输入q结束程序：")
if count == 0:
    result = 0
else :
    result = sum / count
print("您输入的数字平均值为" + str(result))


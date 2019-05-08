import pickle

f_in = open('raw_record.p', 'r')

loading = True
plans = []
raw_plans = []
x_max = -1; x_min = 4096
y_max = -1; y_min = 4096
while loading:
    try:
        raw_plan = pickle.load(f_in)

        for i in raw_plan:
            if isinstance(i, float):
                continue
            raw_plans.append([i[0], i[1], i[2], i[3]]) #[s, o, r, s']
            for j in range(len(i[0])/3):
                x = i[0][j*3]
                x_prime = i[3][j*3]
                y = i[0][j*3+1]
                y_prime = i[3][j*3+1]
                if x > x_max:
                    x_max = x
                if x_prime > x_max:
                    x_max = x_prime
                if y > y_max:
                    y_max = y
                if y_prime > y_max:
                    y_max = y_prime

                if x < x_min:
                    x_min = x
                if x_prime < x_min:
                    x_min = x_prime
                if y < y_min:
                    y_min = y
                if y_prime < y_min:
                    y_min = y_prime
    except EOFError:
        break

f_in.close()

print 'load ' + str(len(raw_plans)) + ' trials'
print 'minimum x: ' + str(x_min) + 'maximum x: ' + str(x_max)
print 'minimum y: ' + str(y_min) + 'maximum y: ' + str(y_max)

# scale to [-1, 1]
x_scale = 2.0/(x_max - x_min)
y_scale = 2.0/(y_max - y_min)
offset = -1.0
new_plans = []
for i in raw_plans:
    s = ()
    s_prime = ()
    for j in range(len(i[0])/3):
        s_x = i[0][j*3] * x_scale + offset
        s_y = i[0][j*3+1] * y_scale + offset
        sp_x = i[3][j*3] * x_scale + offset
        sp_y = i[3][j*3+1] * y_scale + offset
        s += (s_x, s_y, i[0][j*3+2],)
        s_prime += (sp_x, sp_y, i[3][j*3+2],)
    new_plans.append((s, i[1], i[2], s_prime))

print new_plans

f_out = open('record.p', 'w')
pickle.dump(new_plans, f_out)
f_out.close()
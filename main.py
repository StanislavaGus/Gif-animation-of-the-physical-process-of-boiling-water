from PIL import Image, ImageDraw
import random
import math

center_x, center_y = 0,0

left_bottom_point, left_top_point, right_top_point, right_bottom_point = (0,0), (0,0), (0,0), (0,0)

def is_inside_quadrilateral(point):
    global left_bottom_point, left_top_point, right_top_point, right_bottom_point
    A, B, C, D = left_bottom_point, left_top_point, right_top_point, right_bottom_point

    # Векторы сторон четырехугольника
    AB = (B[0] - A[0], B[1] - A[1])
    BC = (C[0] - B[0], C[1] - B[1])
    CD = (D[0] - C[0], D[1] - C[1])
    DA = (A[0] - D[0], A[1] - D[1])

    # Векторы от вершин к точке
    AP = (point[0] - A[0], point[1] - A[1])
    BP = (point[0] - B[0], point[1] - B[1])
    CP = (point[0] - C[0], point[1] - C[1])
    DP = (point[0] - D[0], point[1] - D[1])

    # Векторные произведения
    cross_AB_AP = AB[0] * AP[1] - AB[1] * AP[0]
    cross_BC_BP = BC[0] * BP[1] - BC[1] * BP[0]
    cross_CD_CP = CD[0] * CP[1] - CD[1] * CP[0]
    cross_DA_DP = DA[0] * DP[1] - DA[1] * DP[0]

    # Если все векторные произведения одного знака, то точка внутри четырехугольника
    if (cross_AB_AP >= 0 and cross_BC_BP >= 0 and cross_CD_CP >= 0 and cross_DA_DP >= 0) or \
            (cross_AB_AP <= 0 and cross_BC_BP <= 0 and cross_CD_CP <= 0 and cross_DA_DP <= 0):
        return True
    else:
        return False


def draw_bubble(image, position, radius):
    draw = ImageDraw.Draw(image)
    draw.ellipse([(position[0]-radius, position[1]-radius),
                  (position[0]+radius, position[1]+radius)],
                 fill=(176, 196, 222, 10))
    del draw

def generate_bubbles(image_size, num_bubbles):
    global center_x, center_y, left_bottom_point, left_top_point, right_top_point, right_bottom_point
    bubbles = []

    center_x, center_y = image_size[0] // 2 - 50, image_size[1] / 2 - 70
    square_size = min(image_size[0], image_size[1]) - 200

    left_bottom_point = (410,790)
    left_top_point = (490,100)
    right_top_point = (1330, 100)
    right_bottom_point = (1420,800)

    for _ in range(num_bubbles):
        x = random.randint(center_x - square_size // 2 - 80, center_x + square_size // 2 + 80)
        y = random.randint(center_y - square_size // 2 + 30, center_y + square_size // 2 - 50)

        if (is_inside_quadrilateral((x, y))):
            #radius = random.randint(1, 2)
            radius = random.uniform(0.1, 0.3)
            #radius = 0.1
            bubbles.append({"position": (x, y), "radius": radius})

    return bubbles

def animate_bubbles(image, bubbles, num_big_bubbles_under_surface):
    global center_x, center_y
    frames = []
    angle_radians = 0
    lifting_distance = 0

    big_bubbles_in_water = []
    big_bubbles_under_surface = []

    for frame_num in range(20):  # 30 frames animation
        print('frame - ', frame_num)
        current_frame = image.copy()

        if frame_num % 3 == 0:
            new_bubbles = [{"position": (random.randint(center_x - 280, center_x - 100), 800),
                            "radius": random.randint(3, 8)} for _ in range(1)]
            big_bubbles_in_water.extend(new_bubbles)

        for bubble in bubbles:

            distance = math.sqrt((bubble["position"][0] - center_x) ** 2 + (bubble["position"][1] - center_y) ** 2)

            # Переводим угол из градусов в радианы
            angle_radians -= math.radians(0.1) #random.uniform(0.5, 0.8)

            # Вычисляем новые координаты точки
            new_x = center_x + distance * math.cos(angle_radians)
            new_y = center_y + distance * math.sin(angle_radians)

            if is_inside_quadrilateral((new_x, new_y)):
                draw_bubble(current_frame, (new_x, new_y), bubble["radius"])

        arr_big_bubble_to_pop = []
        for i, big_bubble in enumerate(big_bubbles_in_water):

            lifting_distance = random.randint(-60,-30)
            dx = random.uniform(-1.5,1.5)

            new_x = big_bubble["position"][0] + dx
            new_y = big_bubble["position"][1] + lifting_distance

            if new_y > 100:
                big_bubble["position"] = (big_bubble["position"][0], new_y)
                draw_bubble(current_frame, (new_x, new_y), big_bubble["radius"])
            else:
                big_bubbles_under_surface.append({"position": (new_x, 100), "radius": big_bubble["radius"]})
                arr_big_bubble_to_pop.append(i)

                if len(big_bubbles_under_surface) > num_big_bubbles_under_surface:
                    big_bubbles_under_surface.pop(0)

        for big_bubble_surf in big_bubbles_under_surface:

            if big_bubble_surf["position"][0] < center_x:
                dx = random.uniform(-1.5, -0.5)
            else:
                dx = random.uniform(0.5, 1.0)

            new_x = big_bubble_surf["position"][0] + dx
            draw_bubble(current_frame, (new_x, big_bubble_surf["position"][1]), big_bubble_surf["radius"])

        tmp_bubles = []
        for j in range(len(big_bubbles_in_water)):
            if not (j in arr_big_bubble_to_pop):
                tmp_bubles.append(big_bubbles_in_water[j])
        big_bubbles_in_water = tmp_bubles

        frames.append(current_frame)
    return frames

def save_animation(frames, output_filename):
    frames[0].save(output_filename, save_all=True, append_images=frames[1:], loop=0, duration=80)

# Load the PNG image
input_image = Image.open("input_image.png")

# Generate bubbles
bubbles = generate_bubbles(input_image.size, num_bubbles=70000)

# Create animated frames
animated_frames = animate_bubbles(input_image, bubbles, num_big_bubbles_under_surface=3)

# Save the animation
save_animation(animated_frames, "animated_bubbles.gif")

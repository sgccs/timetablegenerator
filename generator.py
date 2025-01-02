import re
import pdfplumber
import pygame
import re
import time as t
import os


script_dir = os.path.dirname(os.path.abspath(__file__))

time_pdf_path = os.path.join(script_dir, "time.pdf")
example_pdf_path = os.path.join(script_dir, "example.pdf")

pygame.init()

def extract_times(input_text, time_str="5:25"):
    lines = input_text.splitlines()
    time_pattern = re.compile(r'\d{1,2}:\d{2}')
    times = []
    for line in lines:
        if time_str in line:
            times = re.findall(time_pattern, line)
            break

    return times

def extract_schedule_after_525(input_text):
    lines = input_text.splitlines()
    for index, line in enumerate(lines):
        if '5:25' in line:
            return lines[index+1:]
    return []

def map_timetable(day,row,slot_freq):
    row = row//3
    for i in range(len(day)-1,-1,-1):
        temp = day[i].split()
        if(i == 0):
            lab_slots[temp[0]] = timetable[row][1:4]
            lab_slots[temp[1]] = timetable[row][-3:]
        elif(i == 1):
            # first col/ morning class
            timetable[row][0] = temp[i]+str(slot_freq.get(temp[i],1))
            slot_freq[temp[i]]=slot_freq.get(temp[i],1) + 1
        else:
            # rest all
            for i in range(len(temp)):
                timetable[row][i+1] = temp[i]+str(slot_freq.get(temp[i],1))
                slot_freq[temp[i]]=slot_freq.get(temp[i],1) + 1

time = []
with pdfplumber.open(time_pdf_path) as pdf:
    for page in pdf.pages:
        time.append(page.extract_text()) 

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
times = extract_times(time[0],time_str="8:30") 
timetable = [['' for _ in range(len(times))] for _ in range(len(weekdays))]
lab_slots = {}
schedule = extract_schedule_after_525(time[0])
slot_freq = {}
for i in range(0,len(schedule),3):
    map_timetable(schedule[i:i+3],i,slot_freq)

 
def ext(input_str):
    pattern = r"([A-Za-z0-9]+)\\([A-Za-z0-9\-]+)"
    matches = re.match(pattern, input_str)
    if matches:
        letter = []
        if(len(matches.group(1)) == 1 ):
            if(not lab_slots.get(matches.group(1))):
                for i in range(1,4):
                    letter.append(matches.group(1) + str(i))
            else:
                letter.append(lab_slots[matches.group(1)])
        elif(len(matches.group(1)) == 2 ):
            if(not lab_slots.get(matches.group(1)[0])):
                letter.append(matches.group(1))
            else:
                letter.append(lab_slots[matches.group(1)[0]][int(matches.group(1)[1])-1])
        elif(len(matches.group(1)) == 3 ):
            if(not lab_slots.get(matches.group(1)[0])):
                for i in range(1,4):
                    if(str(i) in matches.group(1)):
                        letter.append(matches.group(1)[0] + str(i))    
            else:
                letter.append(lab_slots[matches.group(1)[0]][int(matches.group(1)[1])-1])
                letter.append(lab_slots[matches.group(1)[0]][int(matches.group(1)[2])-1])      
        else:
            for i in matches.group(1):
                if(not lab_slots.get(i)):
                    for _ in range(1,4):
                        letter.append(i + str(_))
                else:
                    letter.append(lab_slots[i])   
        return letter
    else:
        return []

    
all_data = []
with pdfplumber.open(example_pdf_path) as pdf:
    # Iterate over each page
    for page in pdf.pages:
        # Extract the tables from the page
        tables = page.extract_tables()
        
        # Iterate over each table
        for table in tables:
            for row in range(1,len(table)):
                m = table[row]
                slot = []
                slot += ext(m[5]) # lec
                slot += ext(m[6]) # tut
                slot += ext(m[7]) # lab
                if(slot):
                    all_data.append(
                        {
                            "course_code": m[0],
                            "course_name": m[1].strip(),
                            "credits": m[3],
                            "discipline": m[4],
                            "slot": slot,  # ['A1', 'A2', 'A3']
                        }
                    )

course_slot_table = {i["course_code"] : i["slot"] for i in all_data}


def check_feq_slots(result,selected_courses):
    cnt = 0
    slot = course_slot_table[result.split(":")[0]] # ['A1', 'A2', 'A3']
    for i in selected_courses:
        if(slot and len([x for x in course_slot_table[i.split(":")[0]] if x in slot])!=0):
            cnt+=1
    return cnt

pygame.init()

# Screen setup
screen_info = pygame.display.Info()
screen_width = screen_info.current_w - 100
screen_height = screen_width // 2
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Class Timetable")

# Fonts
font = pygame.font.SysFont("Arial", 20)
header_font = pygame.font.SysFont("Arial", 25)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Weekdays and timetable placeholder

# Variables for search bar and button
search_query = ""
show_timetable = False
searchable_items = [(course["course_code"], course["course_name"]) for course in all_data]
matching_results = []
selected_courses = []
dropdown_active = False
cursor_visible = True
cursor_blink_time = 500  # milliseconds
scroll_offset = 0
scroll_speed = 20  
max_scroll_offset = 0
scroll_offset_selected = 0
scroll_speed_selected = 20
max_scroll_offset_selected = 0
last_blink_time = pygame.time.get_ticks()


def update_timetable():
    temp = [['' for _ in range(len(times))] for _ in range(len(weekdays))]
    for row in range(len(temp)):
        for col in range(len(temp[row])):
            for i in selected_courses:
                if(timetable[row][col] in course_slot_table[i.split(":")[0]]):
                    temp[row][col]+= i.split(":")[0]
    return temp

# Function to draw text on the screen
def draw_text(text, x, y, font, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))



# Function to draw the timetable
def draw_timetable(curr_timetable):
    screen.fill(WHITE)
    cell_width = screen_width // (len(times) + 1)
    cell_height = screen_height // (len(weekdays) + 1)

    # Draw headers
    for i, time in enumerate(times):
        pygame.draw.rect(screen, GRAY, (i * cell_width + cell_width, 0, cell_width, cell_height))
        draw_text(time, i * cell_width + cell_width + 5, 5, header_font)

    for i, day in enumerate(weekdays):
        pygame.draw.rect(screen, GRAY, (0, (i + 1) * cell_height, cell_width, cell_height))
        draw_text(day, 5, (i + 1) * cell_height + 5, header_font)

    # Draw grid lines and fill timetable cells
    for i in range(len(weekdays)):
        for j in range(len(times)):
            pygame.draw.rect(screen, WHITE, (j * cell_width + cell_width, (i + 1) * cell_height, cell_width, cell_height))
            if curr_timetable[i][j]:  # If there's a course scheduled
                draw_text(curr_timetable[i][j], j * cell_width + cell_width + 5, (i + 1) * cell_height + 5, font)
            pygame.draw.line(screen, BLACK, (j * cell_width + cell_width, (i + 1) * cell_height),
                             (j * cell_width + cell_width, (i + 2) * cell_height), 2)

    for i in range(len(times) + 1):
        pygame.draw.line(screen, BLACK, (i * cell_width, 0), (i * cell_width, screen_height), 2)

    for i in range(len(weekdays) + 1):
        pygame.draw.line(screen, BLACK, (0, i * cell_height), (screen_width, i * cell_height), 2)

# Visual scroll indicators
def draw_scroll_indicator(x, y, width, height, total_items, visible_items, scroll_offset, item_height):
    # Check if scrolling is needed
    if total_items > visible_items:
        pygame.draw.rect(screen, GRAY, pygame.Rect(x + width - 10, y, 10, height))  # Scrollbar background
        scrollable_height = height  # Space for the scrollbar
        scrollbar_height = max(20, scrollable_height * visible_items // total_items)  # Min scrollbar size
        scrollbar_y = y + (scrollable_height - scrollbar_height) * (scroll_offset / max(1, (total_items - visible_items) * item_height))
        pygame.draw.rect(screen, BLACK, pygame.Rect(x + width - 10, scrollbar_y, 10, scrollbar_height))  # Scrollbar

# Main event loop
running = True
while running:
    screen.fill(WHITE)

    current_time = pygame.time.get_ticks()
    if current_time - last_blink_time > cursor_blink_time:
        cursor_visible = not cursor_visible
        last_blink_time = current_time
    # Search bar
    draw_text("Search for a course:", 20, 20, font)
    pygame.draw.rect(screen, GRAY, pygame.Rect(20, 50, 800, 30))
    draw_text(search_query, 25, 55, font)

    if cursor_visible and len(search_query) < 11:  
        cursor_x = 25 + font.size(search_query)[0]
        pygame.draw.line(screen, BLACK, (cursor_x, 55), (cursor_x, 75), 2)
    elif(len(search_query) == 11):
        cursor_visible = False

    if search_query:
        matching_results = [
            f"{code}: {name}" 
            for code, name in searchable_items 
            if (search_query.lower() in code.lower() or search_query.lower() in name.lower()) 
            and f"{code}: {name}" not in selected_courses and check_feq_slots(f"{code}: {name}",selected_courses)<1
        ]

        dropdown_active = True if matching_results else False
    else:
        dropdown_active = False

    if dropdown_active:
        max_scroll_offset = max(0, len(matching_results) * 35 - 200)  # Limit scroll range
        visible_results = matching_results[scroll_offset // 35 : (scroll_offset // 35) + 6]  # Adjust visible items
        dropdown_y = 90  # Position below the search bar
        for result in visible_results:  # Show up to 5 results
            pygame.draw.rect(screen, GRAY, pygame.Rect(20, dropdown_y, 800, 30))
            draw_text(result, 25, dropdown_y + 5, font)
            
            # add button
            add_button = pygame.Rect(850, dropdown_y, 100, 30)
            pygame.draw.rect(screen, GREEN, add_button)
            draw_text("Add", 870, dropdown_y, font)
            if event.type == pygame.MOUSEBUTTONDOWN and add_button.collidepoint(event.pos):
                if result not in selected_courses and check_feq_slots(result,selected_courses)<1  :
                    selected_courses.append(result)
                t.sleep(0.2)           
            dropdown_y += 35
        draw_scroll_indicator(20, 90, 800, 200, len(matching_results), 6, scroll_offset, 35)

    max_scroll_offset_selected = max(0, len(selected_courses) * 30 - 200)  # Adjust scroll range
    visible_selected_courses = selected_courses[scroll_offset_selected // 30 : (scroll_offset_selected // 30) + 6]  # Adjust visible items
    selected_y = 340  # Position for the first selected course
    for course in visible_selected_courses:
        draw_text(course, 25, selected_y, font)
        # delete button
        delete_button = pygame.Rect(825, selected_y, 100, 30)
        pygame.draw.rect(screen, RED, delete_button)
        draw_text("Delete", 830, selected_y, font)
        if event.type == pygame.MOUSEBUTTONDOWN and delete_button.collidepoint(event.pos):
            if course in selected_courses:
                selected_courses.remove(course)
            t.sleep(0.2) 
        selected_y += 35

    draw_scroll_indicator(20, 340, 800, 200, len(selected_courses), 6, scroll_offset_selected, 30)  

    # Submit button
    submit_button = pygame.Rect(screen_width - 120, 50, 100, 30)
    pygame.draw.rect(screen, GRAY, submit_button)
    draw_text("Submit", screen_width - 110, 55, font)


    # Display timetable if the button is clicked
    if show_timetable:
        curr_timetable = update_timetable()
        draw_timetable(curr_timetable)

    pygame.display.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                search_query = search_query[:-1]
            else:
                if(len(search_query)<=10):
                    search_query += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if submit_button.collidepoint(event.pos):
                show_timetable = True  
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()  # Get the current mouse position
            if 20 <= mouse_x <= 620 and 90 <= mouse_y <= 290:  # Scroll in dropdown area
                scroll_offset -= event.y * scroll_speed
                scroll_offset = max(0, min(scroll_offset, max_scroll_offset))
            elif 20 <= mouse_x <= 620 and 340 <= mouse_y <= 540:  # Scroll in selected courses area
                scroll_offset_selected -= event.y * scroll_speed_selected
                scroll_offset_selected = max(0, min(scroll_offset_selected, max_scroll_offset_selected))


pygame.quit()



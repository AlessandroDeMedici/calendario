import icalendar
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import random
import pytz
import itertools
from pdf2image import convert_from_path

rome = pytz.timezone('Europe/Rome')

colors = [(231/255, 76/255, 60/255), (230/255, 126/255, 34/255), (241/255, 196/255, 15/255),(46/255, 204/255, 113/255),(26/255, 188/255, 156/255),(52/255, 152/255, 219/255),(155/255, 89/255, 182/255),(52/255, 73/255, 94/255)]


def parse_ics(file_path):
    with open(file_path, 'rb') as f:
        cal_data = f.read()
    
    cal = icalendar.Calendar.from_ical(cal_data)
    events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary')
            location = component.get('location', 'Location not specified')
            start_time = component.get('dtstart').dt.astimezone(rome)
            end_time = component.get('dtend').dt.astimezone(rome)
            events.append((summary, location, start_time, end_time))

    return events

def generate_calendar_pdf(events):
    pdf_file = "calendar.pdf"
    c = canvas.Canvas(pdf_file, pagesize=(800,800))

    # Set up the page
    c.setFont("Helvetica-Bold", 14)  # Use a bold font and increase font size
    width, height = 800,800

    # Define the days of the week
    days_of_week = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']

    # Define different color for every lecture
    teacher_colors = dict(zip(set([teacher for teacher, _, _, _ in events]), itertools.cycle(colors)))

    # Draw a time grid for the hours between 8 AM and 8 PM
    for i in range(8, 21):
        c.setStrokeColorRGB(189/255, 195/255, 199/255)
        c.line(10,height - 80 - (i - 8) * 60, width - 10, height - 80 - (i - 8) * 60)


    # Iterate over events and draw on the calendar
    for day_index, day in enumerate(days_of_week):

        # Draw the day label
        c.setStrokeColorRGB(1,1,1)
        c.setFont("Helvetica-Bold",20)


        # Draw the shadow
        c.setFillColorRGB(0.3,0.3,0.3,alpha=0.5)
        c.drawString( ((width - 20)/5) * day_index + 52.5 - 2, height - 50 - 2 , day)

        

        c.setFillColorRGB(0,0,0,alpha=1)
        c.drawString( ((width - 20)/5) * day_index + 52.5, height - 50, day)
        c.setFont("Helvetica-Bold",16)
        

        for event in events:
            name, location, start_time, end_time = event
            day_of_week = start_time.weekday()

            if day_of_week == day_index and 8 <= start_time.hour < 20:
                # Calculate position and size of the event box
                x = 10 + day_index * (width - 20) / 5
                y = height - 80 - (start_time.hour - 8 + start_time.minute / 60) * 60
                event_width = (width - 20) / 5
                event_height = (end_time - start_time).seconds / 3600 * 60
                y -= event_height


                # Draw the event box
                
                c.setFillColorRGB(*teacher_colors[name],alpha=0.6)
                c.roundRect(x, y, event_width, event_height, radius=3, fill=True)
                c.setFillColorRGB(0,0,0,alpha=0.2)
                c.roundRect(x,y,4,event_height,radius=3,fill=True)
                c.setFillColorRGB(*teacher_colors[name],alpha=0.6)

                # Draw the time on the left side
                c.setFillColorRGB(1, 1, 1)  # White text
                time_text = start_time.strftime('%H:%M') + ' - ' + end_time.strftime('%H:%M')
                c.setFont("Helvetica-Bold",16)
                fill_color = teacher_colors[name]
                text_color = tuple(max(0, comp - 0.5) for comp in fill_color)
                c.setFillColorRGB(*text_color)
                c.drawString(x + event_width/2 - 50, y + event_height - 20, time_text)

                # Draw the event text within the box with automatic indentation
                text_lines = [f"{name}",f"{location}"]


                # Indent and draw each line
                #for line_index, line in text_lines:
                #    c.setFillColorRGB(1, 1, 1)
                #    c.drawString(x + 5, y + event_height - 30 - line_index * 15, line)
                nline = 1
                text_object = c.beginText(x + 2.5, y + event_height - 37.5)
                text_object.setFont("Helvetica-Bold", 14)
                fill_color = teacher_colors[name]
                text_color = tuple(max(0, comp - 0.5) for comp in fill_color)
                c.setFillColorRGB(*text_color)
                for line in text_lines:
                    nline += 1
                    current_line = ""
                    words = line.split(" ")
                    for word in words:
                        if len(current_line + ' ' + word) * 8 > event_width - 14:
                            text_object.textLine(current_line)
                            nline += 1
                            current_line = ""
                        current_line += ' ' + word
                        if nline * 16 + 10 >= event_height:
                            break
                    if nline * 16 + 10 >= event_height:
                        break
                    text_object.textLine(current_line)

                c.drawText(text_object)

    c.save()
    print(f"Calendar saved to {pdf_file}")

if __name__ == "__main__":
    ics_file_path = "calendario.ics"  # Replace with the path to your ICS file
    events = parse_ics(ics_file_path)
    generate_calendar_pdf(events)
    images = convert_from_path("./calendar.pdf")
    images[0].save("calendar.png","PNG")


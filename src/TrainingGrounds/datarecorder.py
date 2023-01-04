import csv
from botnet import BotNet


class DataRecorder:
    def __init__(self, view_radius, file_name='data.csv'):
        self.move_buffer = []
        self.buffer_size = 20
        self.file_name = file_name
        self.view_radius = view_radius

    def record_move(self, level, previous_position, new_position, original_direction, new_direction, died, ate_food):
        # anon object
        data = {
            'view': [],
            'direction': original_direction,
            'new_direction': new_direction,
            'died': died,
            'ate': ate_food
        }

        for x in range(-self.view_radius, self.view_radius):
            for y in range(-self.view_radius, self.view_radius):
                
                pos = [previous_position[0] + x,
                     previous_position[1] + y]
                    
                entity = level.at(pos)

                val = BotNet.entity_to_float(entity, level)

                data['view'].append(val)

        self.move_buffer.append(data)

        if len(self.move_buffer) > self.buffer_size:
            data = self.move_buffer.pop(0)
            self.write_data_line(data)
        
        HALF_BUFFER = int(self.buffer_size / 2)

        if len(self.move_buffer) == self.buffer_size:
            if self.move_buffer[HALF_BUFFER]['ate']:
                any_dead = False
                for data in self.move_buffer:
                    if data['died']:
                        any_dead = True
                        break
                
                if any_dead:
                    self.move_buffer = []
                    return
                
                for data in self.move_buffer:
                    self.write_data_line(data)

    def clear(self):
        # write empty csv line
        with open(self.file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([])
            
        self.move_buffer = []

    def write_data_line(self, data):
        row = self.convert_to_csv_row(data)
        with open(self.file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    def convert_to_csv_row(self, data):
        row = []
        row.extend(BotNet.direction_to_floats(data['direction']))
        row.extend(data['view'])
        row.extend(BotNet.direction_to_floats(data['new_direction']))
        return row

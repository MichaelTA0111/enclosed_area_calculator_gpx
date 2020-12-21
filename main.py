from GpxReader import GpxReader, print_statistics


if __name__ == '__main__':
    # Type in the complete file paths of the gpx files in quotes
    # Use .\\ for a relative path to the main.py
    file_paths = ['.\\gpx\\test_line.gpx',
                  '.\\gpx\\test_mission.gpx']

    # Type in the desired file names for the graphs in quotes, including the file format such as .svg or .eps
    # If you dont want the graphs, you put a # at the beginning of lines 12, 13, and 16
    graph_names = ['.\\figures\\lines.svg',
                   '.\\figures\\area.svg']

    slm = GpxReader(file_paths)  # slm stands for straight line mission
    slm.plotter(graph_names)  # Plots graphs using both the lines
    print_statistics(slm)  # Outputs the line distance, area, and average deviation

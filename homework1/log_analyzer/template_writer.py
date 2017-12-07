def write_report_to_template(json_data, template_filename, report_filename):
    with open(template_filename, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('$table_json', json_data)

    # Write the file out again
    with open(report_filename, 'w') as report_file:
        report_file.write(filedata)

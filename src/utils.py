import csv
import json
import logging
import os


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename="logs/run.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )


def save_to_csv(people_data, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Age', 'City', 'State', 'Phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for person in people_data:
            phones = person.get('Phones', [])

            if phones:
                for phone in phones:
                    writer.writerow({
                        'Name': person.get('Name', 'N/A'),
                        'Age': person.get('Age', 'N/A'),
                        'City': person.get('City', 'N/A'),
                        'State': person.get('State', 'N/A'),
                        'Phone': phone
                    })
            else:
                writer.writerow({
                    'Name': person.get('Name', 'N/A'),
                    'Age': person.get('Age', 'N/A'),
                    'City': person.get('City', 'N/A'),
                    'State': person.get('State', 'N/A'),
                    'Phone': 'N/A'
                })


def save_invalid_records(invalid_records, output_csv="output/invalid_records.csv"):
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Age', 'City', 'State', 'Phones', 'Errors']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in invalid_records:
            record = item["record"]
            writer.writerow({
                'Name': record.get('Name', 'N/A'),
                'Age': record.get('Age', 'N/A'),
                'City': record.get('City', 'N/A'),
                'State': record.get('State', 'N/A'),
                'Phones': ", ".join(record.get('Phones', [])),
                'Errors': "; ".join(item.get('errors', []))
            })


def save_summary(summary, output_path="output/run_summary.json"):
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=4)
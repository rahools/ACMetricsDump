# Assetto Corsa Metric Dump

Assetto Corsa Metric Dump is an application designed to help Assetto Corsa users record car state as metrics. The metrics are currently only dumped in CSV file format. The roadmap includes dumping the metrics in a database or streaming to Apache Kafka, making it easy to analyze the performance data.

## Features

- Records car state as metrics
- Dumps metrics in CSV file

## Installation

1. Go to the installation folder of Assetto Corsa, then navigate to `apps/python`
2. Clone or extract the repository in this folder
3. Enable `acMetricsDump` in Assetto Corsa settings
4. Enable `acMetricsDump` in the session

## Usage

1. Run Assetto Corsa
2. Start recording the car state metrics
3. The recorded metrics will be automatically dumped as a CSV file

## Output

To view the output, go to the same folder as the installation folder. There will be multiple CSV files, with the naming format: `metricdump_{car_name}_{track_name}_{session_start_time}.csv`

## Contributing

Contributions are welcome and greatly appreciated. To contribute, please fork the repository, make your changes, and submit a pull request.

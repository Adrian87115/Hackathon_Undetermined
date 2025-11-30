from data_processor import excel_to_json, semicolon_csv_to_json, convert_csv
import eco_gpt as eco

def main():
    # excel_to_json("data/work.xlsx", "data/work.json")
    # semicolon_csv_to_json("../Datasets/hakaton.csv", "../Datasets/hakaton.json")
    # semicolon_csv_to_json("../Datasets/trivial_prompts_polite.csv", "../Datasets/trivial_prompts_polite.json")
    # convert_csv("data/my_data.txt", "data/my_data.csv")

    model = eco.ECOGPT(dataset_path = "../Datasets/merged.json", batch_size = 32, sequence_length = 64)
    model.train()

    # model = eco.ECOGPT(checkpoint = "models/eco_gpt_20.pth", batch_size = 64, sequence_length = 64)
    # eco.convert(model)

if __name__:
    main()
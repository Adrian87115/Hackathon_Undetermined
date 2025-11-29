from data_processor import excel_to_json, semicolon_csv_to_json
import eco_gpt as eco

def main():
    # excel_to_json("data/work.xlsx", "data/work.json")
    # semicolon_csv_to_json("data/hakaton.csv", "data/hakaton.json")
    # semicolon_csv_to_json("../Datasets/trivial_prompts_polite.csv", "data/trivial_prompts_polite.json")

    model = eco.ECOGPT(dataset_path = "data/hakaton.json", train_mode = 1, batch_size = 16, total_batch_size = 128 * 16, sequence_length = 64)
    model.train()
    # model.evaluate()

    # model = eco.ECOGPT(checkpoint = "models/eco_gpt_1.pth")
    # eco.convert(model)

if __name__:
    main()
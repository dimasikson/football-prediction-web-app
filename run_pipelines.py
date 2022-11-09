from src.pipelines.update import refresh_fixtures, refresh_results, preprocess_results, generate_predictions
from src.utils.functions import get_partitions
from src.utils.config import Config as cfg


if __name__ == "__main__":
    train_partitions = get_partitions(cfg.FIRST_SEASON, cfg.CURRENT_SEASON - 1)
    test_partitions = get_partitions(cfg.CURRENT_SEASON - 1, cfg.CURRENT_SEASON)
    valid_partitions = get_partitions(cfg.CURRENT_SEASON, cfg.CURRENT_SEASON + 1)

    refresh_fixtures()
    # refresh_results(train_partitions)
    # refresh_results(test_partitions)
    refresh_results(valid_partitions)

    # preprocess_results(train_partitions, "train")
    # preprocess_results(test_partitions, "test")
    preprocess_results(valid_partitions, "valid", add_fixtures=True)

    generate_predictions("valid")

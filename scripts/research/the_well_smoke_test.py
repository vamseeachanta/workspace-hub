
from the_well.data import WellDataset
import torch
from torch.utils.data import DataLoader

def smoke_test():
    print("Starting The Well smoke test...")
    try:
        # We'll use a small dataset like active_matter for the test
        # We only want to see if the metadata and first batch can be streamed
        print(f"Initializing WellDataset with name: active_matter...")
        trainset = WellDataset(
            well_base_path="hf://datasets/polymathic-ai/",
            well_dataset_name="active_matter",
            well_split_name="train",
        )
        print("Dataset object created successfully.")
        
        print("Creating DataLoader...")
        train_loader = DataLoader(trainset, batch_size=1)
        print("DataLoader created.")
        
        print("Fetching first batch from the stream...")
        for i, batch in enumerate(train_loader):
            print(f"Successfully fetched batch {i+1}!")
            print(f"Batch keys: {batch.keys()}")
            break
        print("Smoke test PASSED.")
    except Exception as e:
        print(f"Smoke test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    smoke_test()

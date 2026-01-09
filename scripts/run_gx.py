import great_expectations as gx
import sys
import os

def run_gx():
    print("🏃 Running Great Expectations Checkpoint...")
    context = gx.get_context(context_root_dir=os.path.join(os.getcwd(), "gx"))
    
    checkpoint_name = "checkpoint_critical"
    
    results = context.run_checkpoint(checkpoint_name=checkpoint_name)
    
    if not results["success"]:
        print("❌ Validation Failed!")
        # Print breakdown
        for validation_result in results["run_results"].values():
            stats = validation_result["validation_result"]["statistics"]
            print(f"  - Statistics: {stats}")
        sys.exit(1)
    else:
        print("✅ Validation Success!")
        sys.exit(0)

if __name__ == "__main__":
    run_gx()

from momopedia.state import MomoState
from momopedia.main import app  # your compiled workflow

# Step 1: define initial state
initial_state = MomoState(
    topic="History of momo in Nepal",  # example input
    messages=[],                       # conversation history
    iteration=0,
    next_step="author"
)

# Step 2: run the workflow
final_state = app.invoke(initial_state)

# Step 3: inspect results
print("Final state:")
print(final_state)
print("\nFinal article content:")
print(final_state.get("article", "No article generated"))

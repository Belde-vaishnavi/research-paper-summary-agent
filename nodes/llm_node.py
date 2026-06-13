from chains.synthesis_chain import build_synthesis_chain


def llm_node(state: dict) -> dict:
    """Synthesize all paper analyses into unified summary."""
    try:
        chain = build_synthesis_chain()

        llm_output = chain.invoke({
            "all_summaries": state["cleaned_context"]
        })

        return {
            **state,
            "llm_output": llm_output,
        }
    except Exception as e:
        import traceback
        print(f"✗ Error in LLM synthesis node:")
        print(f"  {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        
        # Return state with error message
        return {
            **state,
            "llm_output": f"[ERROR] Synthesis failed: {str(e)}",
        }
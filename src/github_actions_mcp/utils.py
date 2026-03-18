def format_error(e: Exception) -> str:
    return f"Error ({type(e).__name__}): {e}"

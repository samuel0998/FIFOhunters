from datetime import date

def calculate_fifo(opened_since, expected, received):
    today = date.today()

    # Segurança
    if not opened_since:
        fifo_days = None
        fifo_status = None
    else:
        fifo_days = (today - opened_since).days

        if fifo_days <= 1:
            fifo_status = "green"
        elif fifo_days <= 2:
            fifo_status = "purple"
        elif fifo_days <= 3:
            fifo_status = "yellow"
        elif fifo_days <= 5:
            fifo_status = "orange"
        else:
            fifo_status = "red"

    # Cálculo de recebimento
    difference = (expected or 0) - (received or 0)

    if difference > 0:
        shortage_type = "shortage"
    elif difference < 0:
        shortage_type = "overage"
    else:
        shortage_type = "ok"

    return {
        "fifo_days": fifo_days,
        "fifo_status": fifo_status,
        "difference": difference,
        "shortage_type": shortage_type
    }

import os
import requests
import tqdm


def get_value(value_name, json_data):
    val = json_data.get('data', {}).get(value_name, {}).get('values')
    if len(val):
        val = val[-1]
    else:
        val = None
    return val

def get_values_for_ticket(ticket):
    r = requests.get(f'http://localhost:8000/{ticket}/q?full_info=false&include_data=any').json()
    values = ['p_e', 'roa', 'roe', 'p_e', 'p_s', 'p_b_v', 'ev_ebitda', 'i_r_r', 'revenue', 'ebitda', 'capex', 'opex',
              'e_v', 'eps']
    values = ['p_e', 'roa', 'ebitda', 'ev_ebitda', 'capex']
    results = {}
    for val in values:
        results[val] = get_value(value_name=val, json_data=r)
    return results



def ranking(ranking_list):
    # list_tickets_for_rank = df['ticker'].unique().tolist()

    """Тут быет выполняться ранжирование по акциям компаний
    из которых бот будет потом выбирать лучших кандидатов"""
    rating = {}
    for ticket in ranking_list:
        rating[ticket] = 0
    print('я тут ')
    info_list = [(ticket, get_values_for_ticket(ticket)) for ticket in tqdm.tqdm(ranking_list[:10])]
    print('я тут 2')
    list_metrics = []
    for metric in tqdm.tqdm(['p_e', 'roa', 'ebitda', 'ev_ebitda', 'capex']):
        try:
            temp_list = [(x[0], float(x[1].get(metric, 0))) if x[1].get(metric, 0) else (x[0], 0) for x in info_list]
        except:
            continue
        # чем больше тем лучше
        if metric in ['roa', 'ebitda', 'ev_ebitda']:
            sorted_list = sorted(temp_list, key=lambda x: -x[1])
        else:
            sorted_list = sorted(temp_list, key=lambda x: x[1])
        for point, list_ in enumerate(sorted_list):
            rating[list_[0]] += point
        # pbar.update(10)

    list_metrics = []
    result_list_sorted = sorted(ranking_list, key=lambda x: rating[x])[:5]

    for ticket in result_list_sorted:
        info = get_values_for_ticket(ticket)
        list_metrics.append(str([str(ticket), str(info)]))
    metrics = '\n'.join(list_metrics)

    return result_list_sorted, metrics
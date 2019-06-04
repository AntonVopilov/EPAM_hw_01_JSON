
from collections import deque, Counter


def collisions_to_list(counter_dict, name, sort_type='max'):

    if sort_type == 'max':
        max = counter_dict.most_common(1)
        return {name: [item for (i, item) in enumerate(counter_dict) if counter_dict[item] == max[0][1]]}
    if sort_type == 'min':
        min = counter_dict.most_common()[-1][1]
        return {name: [item[0] for (i, item) in enumerate(counter_dict.most_common()[::-1]) if counter_dict[item[0]] == min]}


def my_dump2(obj):

    if obj is None:
        return "null"

    if isinstance(obj, int):
        return str(obj)

    if isinstance(obj, str):
        return '"'+obj+'"'

    if isinstance(obj, list):
        s = ''
        for inner_obj in obj:
            s = ''.join([s, my_dump(inner_obj), ', '])
        return ''.join(['[', s[:-2], ']'])

    if isinstance(obj, dict):
        s = ''
        for key, value in obj.items():
            s = ''.join([s, my_dump(key), ': ', my_dump(value), ', '])
        return ''.join(['{', s[:-2], '}'])

def my_dump(obj):

    if obj is None:
        return "null"

    if isinstance(obj, int):
        return str(obj)

    if isinstance(obj, str):
        return '"'+obj+'"'

    if isinstance(obj, list):
        s = ''
        for inner_obj in obj:
            s += my_dump(inner_obj) + ', '
        return '[' + s[:-2] + ']'

    if isinstance(obj, dict):
        s = ''
        for key, value in obj.items():
            s += my_dump(key) + ': ' + my_dump(value) + ', '
        return '{' + s[:-2] + '}'


def dump_json(obj, file_name):
    with open(file_name, 'w') as file:
        file.write(my_dump(obj))


def str_to_base_obj(s: str, current_type):

    if s == 'null':
        return None, 'None'

    if s.isdigit() and current_type != 'string':
        s_ch = float(s)
        if s_ch.is_integer():
            return int(s_ch), 'int'
        else:
            return s_ch, 'float'

    if s.isalpha() or current_type == 'string' or current_type == 'string_dict':
        return str(s), 'str'


def str_to_obj(s: str, curr_type=None):

    if curr_type != 'string':
        if s == '[':
            return [], 'list_open'

        elif s == '{':
            return {}, 'dict_open'

        elif (s == '"'):
            return '', 'string'

        else:
            return s, 'base_type'
    else:
        return s, 'base_type'




def update_stack(obj, type_obj, stack):

    if type_obj == 'pop':
        buffer = stack.pop()[0]
        curr_type = stack[-1][1]
        append_to_current_object(buffer, curr_type, stack)
        return curr_type

    if type_obj == 'pop_value':
        value = stack.pop()[0]
        key = stack.pop()[0]
        stack[-1][0][key] = value

    else:
        stack.append([obj, type_obj])
        return type_obj


def append_to_current_object(local_obj, curr_type, stack):

    if curr_type == 'list_open' or curr_type == 'stack_level':
        stack[-1][0].append(local_obj)

    if curr_type == 'string' or curr_type == 'key_open' or curr_type == 'value_open':
        stack[-1][0] = local_obj


def read_local_object(local_str, char, curr_type, reading_done=False):

    if reading_done:
        local_str = ''

    if local_str != '' and (char == ',' or char == ']' or char == '}' or char == ':'):

        if curr_type == 'string' and (local_str[-1] == '"'):
            return local_str[:-1], True
        if curr_type != 'string':
            return local_str, True

    if local_str == '' and curr_type != 'string' and (char == ']' or char == '}'):
        return local_str, True

    return local_str + char, False


def parse_json(file_name: str):

    stack = deque([])
    stack.append([[], 'stack_level'])
    local_str = ''
    char = True
    reading_done = False

    with open(file_name, "r") as json_file:
        while bool(char):

            char = json_file.read(1)
            curr_type = stack[-1][1]
            obj, type_obj = str_to_obj(char, curr_type)

            if curr_type != 'string' and (char == ' ' ):
                pass

            if (curr_type == 'list_open' or curr_type == 'value_open' or curr_type == 'dict_open') and local_str == '' and char == ',':
                pass

            elif type_obj != 'base_type':
                curr_type = update_stack(obj, type_obj, stack) # можно возвращать сзесь каррент тип

            else:
                local_str, reading_done = read_local_object(local_str, char, curr_type, reading_done)

                if reading_done:
                    if local_str != '':
                        local_obj = str_to_base_obj(local_str.lstrip(), curr_type)[0]

                        if curr_type == 'string':
                            curr_type = update_stack(obj=None, type_obj='pop', stack=stack)

                        if curr_type == 'dict_open':
                            curr_type = update_stack(None, type_obj='key_open', stack=stack)

                        append_to_current_object(local_obj, curr_type, stack)

                    if curr_type == 'value_open':
                        curr_type = update_stack(None, type_obj='pop_value', stack=stack)


                    if char == ',' and curr_type == 'string':
                        curr_type = update_stack(obj=None, type_obj='pop', stack=stack)

                    if char == ']' or char == '}':
                        if curr_type == 'string':
                            curr_type = update_stack(obj=None, type_obj='pop', stack=stack)

                        curr_type = update_stack(obj=None, type_obj='pop', stack=stack)
                    if char == ':' and curr_type == 'key_open':
                        curr_type = update_stack(None, type_obj='value_open', stack=stack)
                    local_str = ''

        return stack[-1][0][0]


if __name__ == '__main__':

    data_2 = parse_json("winedata_2.json")
    print('done_2')

    data_1 = parse_json("winedata_1.json")
    print('done_1')

    title_set = set()

    data_sum = data_1 + data_2
    data = []
    set_values = set()
    for i, item in enumerate(data_sum):
        val = tuple(item.values())
        if val not in set_values:
            data.append(item)
            set_values.add(val)



    dump_json(data, 'union_wine.json')
    print('dumping done')

    sorts = (r'Gew\u00fcrztraminer', 'Riesling', 'Merlot', 'Tempranillo', 'Red Blend')
    stat_items = ('min_price', 'max_price', 'most_common_country', 'most_common_region', 'avarage_score')
    statistic = {}

    for sort in sorts:
        stat_dict = {}
        for stat_item in stat_items:
            if stat_item == 'min_price':
                stat_dict[stat_item] = float('inf')
            if stat_item == 'max_price':
                stat_dict[stat_item] = -1
            if stat_item == 'most_common_country' or stat_item == 'most_common_region':
                stat_dict[stat_item] = Counter()
            if stat_item == 'avarage_score':
                stat_dict[stat_item] = []
        statistic[sort] = stat_dict

    most_expensive_wine = Counter()
    score_counter = Counter()
    expensive_country = {}
    rated_country = Counter()
    active_commentator = Counter()

    for item in data:
        price_current = item.get('price')
        title = item.get('title')
        score_current = item.get('points')
        country = item.get('country')
        taste_name = item.get('taster_name')

        if taste_name:
            active_commentator.setdefault(taste_name, 1)
            active_commentator[taste_name] += 1

        if country:
            rated_country.setdefault(country, -1)
            if score_current:
                rated_country[country] = max(float(score_current), rated_country[country])
            else:
                rated_country[country] = None
            if price_current:
                expensive_country.setdefault(country, [price_current])
                expensive_country[country].append((price_current))

        if price_current:
            most_expensive_wine[title] = price_current
        if score_current:
            score_counter[title] = score_current

        if any(item['variety'] == sort for sort in sorts):

            wine_sort = item['variety']

            if price_current:
                prices_min = [statistic[wine_sort]['min_price'], price_current]
                statistic[wine_sort]['min_price'] = min(price for price in prices_min if price is not None)
                prices_max = [statistic[wine_sort]['max_price'], price_current]
                statistic[wine_sort]['max_price'] = max(price for price in prices_max if price is not None)

            if item.get('country'):
                statistic[wine_sort]['most_common_country'].setdefault(country, 1)
                statistic[wine_sort]['most_common_country'][country] += 1

            if item.get('region_1'):
                statistic[wine_sort]['most_common_region'].setdefault(item.get('region_1'), 1)
                statistic[wine_sort]['most_common_region'][item.get('region_1')] += 1

            if item.get('region_2'):
                statistic[wine_sort]['most_common_region'].setdefault(item.get('region_2'), 1)
                statistic[wine_sort]['most_common_region'][item.get('region_2')] += 1

            if item.get("points"):
                statistic[wine_sort]['avarage_score'].append(float(item.get('points')))

    for sort in sorts:
        if statistic[sort]['most_common_country']:
            statistic[sort]['most_common_country'] = statistic[sort]['most_common_country'].most_common(1)[0][0]

        if statistic[sort]['most_common_region']:
            statistic[sort]['most_common_region'] = statistic[sort]['most_common_region'].most_common(1)[0][0]

        if len(statistic[sort]['avarage_score']):
            statistic[sort]['avarage_score'] = round(sum(statistic[sort]['avarage_score']) / len(statistic[sort]['avarage_score']))

    expensive_country = Counter({key: round(sum(value)/max(len(value), 1)) for key, value in expensive_country.items()})

    second_stat = {}
    second_stat.update(statistic)

    second_stat.update(collisions_to_list(most_expensive_wine, 'most_expensive_wine'))
    second_stat.update(collisions_to_list(most_expensive_wine, 'cheapest_wine', sort_type='min'))
    second_stat.update(collisions_to_list(score_counter, 'most score wine'))
    second_stat.update(collisions_to_list(score_counter, 'underscore wine', sort_type='min'))
    second_stat.update(collisions_to_list(expensive_country, 'most expensive country'))
    second_stat.update(collisions_to_list(expensive_country, 'cheapest_country', sort_type='min'))
    second_stat.update(collisions_to_list(rated_country, 'most_rated_country'))
    second_stat.update(collisions_to_list(rated_country, 'underrated country', sort_type='min'))
    second_stat.update(collisions_to_list(active_commentator, 'most active commentator'))

    statistics = {'statistics': second_stat}
    dump_json(statistics, 'statistics.json')




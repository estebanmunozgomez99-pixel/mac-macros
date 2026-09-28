import json
d=json.load(open('data/build/data.json'))
si=[i for i,(l,s) in enumerate(d['stations']) if d['locations'][l]=='Centro' and s=='SMPL Rotational Menu'][0]
names={r[1] for r in d['items'] if r[0]==si}
S="Side Salad"
W=[
[ # Week 1
 ["Honey Balsamic Cod","Roasted Pesto Chicken","Flex Beef And Lentil Shepherds Pie","Vegetable Tikka Masala",S,"Zucchini, Peppers And Tomato Saute","Vegetable Rice Pilaf"],
 ["Lemon Caper Basa","Sweet Chili Roasted Chicken Leg","Lamb & Lentil Sausage With Mushroom Sauce","Stuffed Portobello",S,"Honey Glazed Carrots","Coconut Scalloped Potatoes"],
 ["Citrus Glazed Salmon","Orange Ginger Beef Tenderloin","Flex Beef & Lentil Sloppy Joe","Lentil Shepherds Pie",S,"Peppers, Onions And Broccoli","Lemon Basmati Rice"],
 ["Cajun Cod","Piri Piri Chicken Wings","Flex Pork & Lentil Napa Cabbage Roll","Curried Potato And Chickpea Taco (Chana Gobi)",S,"Roasted Cauliflower","Mushroom Onion Rice"],
 ["Pesto Basa","New Orleans Roasted Pork Loin","Flex Italian Style Beef & Lentil Meatballs","Beyond Meat Gnocchi Bolognaise",S,"Roasted Root Vegetables","Caramelized Onion Mashed Potatoes"],
 ["Sweet & Spicy Salmon","Lemon Herb And Garlic Chicken Leg","Yellow Split Pea & Chicken","Mesir Wat",S,"Roasted Kale, Peppers, Broccoli & Onions","Sweet Potato Wedges"],
 ["Garlic Crusted Basa","Slow Roasted Honey Garlic Pork Ribs","Beef & Lentil Moussaka","Samosa Lentil Sweet Potato",S,"Carrot And Corn Medley","Herb Roasted Potatoes"]],
[ # Week 2
 ["Red Thai Salmon","Cajun Chicken Breast","Flex Beef, Lentil & Mushroom Shepherds Pie","Tex-Mex Stuffed Pepper",S,"Roasted Kale, Peppers, Broccoli & Onions","Mushroom Onion Rice"],
 ["Lemon Pepper Basa","Tandoori Chicken Leg","Flex Italian Style Beef & Lentil Meatballs","Spanish Lentil Stew With Gnocchi",S,"Peppers And Green Beans","Herb Roasted Potatoes"],
 ["Firecracker Salmon","Cajun Creole Pork Loin","Beef Burrito Taco","Cauliflower And Bean Tacos",S,"Zucchini, Peppers And Tomato Saute","Black Bean Rice"],
 ["Cilantro Ginger Lime Cod","Jerk Chicken Wings","Meatloaf","Vegetable Lasagna",S,"Steamed Broccoli","Sweet Potato Mash"],
 ["Piri Piri Salmon","Salisbury Steak",'Chicken "Parmesan" Stuffed Spaghetti Squash',"Moussaka Beyond",S,"Roast Parsnips And Carrots","Lemon Garlic Potatoes"],
 ["Bruschetta Basa","Chicken Biryani","Tex-Mex Beef Sweet Potato","Lentil Shepherds Pie",S,"Pepper, Mushroom, & Onions","Turmeric Basmati Rice"],
 ["Brown Sugar Cod","Smoked Paprika Slow Roasted Pork Ribs","Flex Beef & Lentil Kofta","Cauliflower Mac And Cheese",S,"Roasted Broccoli, Cauliflower And Carrots","Roasted Potatoes"]],
[ # Week 3
 ["Lemon Caper Basa","Moroccan Spiced Chicken","Flex Beef & Lentil Sloppy Joe","Samosa Lentil Sweet Potato",S,"Honey Glazed Carrots","Vegetable Rice Pilaf"],
 ["Honey Balsamic Cod","Smoked Paprika Spiced Pork Loin","Yellow Split Pea & Chicken","Lentil Shepherds Pie",S,"Zucchini, Peppers And Tomato Saute","Herb Roasted Potatoes"],
 ["Citrus Glazed Salmon","Tandoori Chicken Leg","Salisbury Steak","Beyond Meat Gnocchi Bolognaise",S,"Peppers, Onions And Broccoli","Lemon Basmati Rice"],
 ["Cajun Cod","Honey Bbq Chicken Wings","Flex Pork & Lentil Napa Cabbage Roll","Vegetable Lasagna",S,"Roasted Cauliflower","Caramelized Onion Mashed Potatoes"],
 ["Pesto Basa","Bbq Chicken Leg","Beef Enchilada Lasagna","Stuffed Portobello",S,"Roasted Root Vegetables","Mushroom Onion Rice"],
 ["Sweet & Spicy Salmon","Jerk Beef With Chimichurri","Veg Noodle Beef Lasagna","Mesir Wat",S,"Roasted Kale, Peppers, Broccoli & Onions","Roasted Potatoes"],
 ["Garlic Crusted Basa","Southern Style Bbq Pork Ribs","Beef Stuffed Pepper","Stuffed Eggplant",S,"Carrot And Corn Medley","Sweet Potato Wedges"]],
[ # Week 4
 ["Red Thai Salmon","Beef Curry",'Chicken "Parmesan" Stuffed Spaghetti Squash',"Vegetable Lasagna",S,"Roasted Kale, Peppers, Broccoli & Onions","Mushroom Onion Rice"],
 ["Lemon Pepper Basa","Red Thai Chicken Leg","Salisbury Steak","Tex-Mex Stuffed Pepper",S,"Peppers And Green Beans","Herb Roasted Potatoes"],
 ["Firecracker Salmon","Tandoori Chicken Taco","Turkey Meatballs","Jackfruit And Lentil Taco",S,"Zucchini, Peppers And Tomato Saute","Black Bean Rice"],
 ["Cilantro Ginger Lime Cod","Buffalo Style Chicken Wings","Flex Beef & Lentil Nachos","Beyond Meat Taco With Pico De Gallo",S,"Steamed Broccoli","Coconut Scalloped Potatoes"],
 ["Piri Piri Salmon","Lemon Pepper Chicken Breast","Flex Pork & Quinoa Pojarski","Cauliflower Mac And Cheese",S,"Roast Parsnips And Carrots","Sweet Potato Mash"],
 ["Bruschetta Basa","Roasted Chicken Leg","Tex-Mex Beef Sweet Potato","Beyond Beef & Tomato Spaghetti Squash",S,"Pepper, Mushroom, & Onions","Turmeric Basmati Rice"],
 ["Brown Sugar Cod","Sweet And Sour Pork Ribs","Flex Beef & Lentil Kofta","Vegan Enchilada",S,"Roasted Broccoli, Cauliflower And Carrots","Roasted Potatoes"]],
]
missing={n for w in W for day in w for n in day if n not in names}
print('missing',missing)
sched={n for w in W for day in w for n in day}
print('unscheduled in data:',sorted(names-sched))
json.dump({"Centro|SMPL Rotational Menu":{"week1Monday":"2026-09-07","weeks":W}},open('data/build/rotation.json','w'),ensure_ascii=False,separators=(',',':'))

from apps.accounts.models import Section

sections_data = [
    # (codename, label, icon, parent_codename, order)
    ('library', 'Library Hub', 'fa-book', None, 1),
    ('library.books', 'Books', 'fa-book-open', 'library', 1),
    ('library.categories', 'Categories', 'fa-tag', 'library', 2),
    ('library.subcategories', 'Sub-Categories', 'fa-tags', 'library', 3),
    ('library.issues', 'Issues', 'fa-clipboard', 'library', 4),
    ('library.fines', 'Fines', 'fa-dollar-sign', 'library', 5),

    ('lab', 'Laboratories', 'fa-flask', None, 2),
    ('lab.equipment', 'Equipment', 'fa-tools', 'lab', 1),
    ('lab.labs', 'Labs', 'fa-vials', 'lab', 2),
    ('lab.categories', 'Categories', 'fa-tags', 'lab', 3),
    ('lab.subcategories', 'Sub-Categories', 'fa-sitemap', 'lab', 4),
    ('lab.bookings', 'Bookings', 'fa-calendar', 'lab', 5),

    ('inventory', 'Inventory control', 'fa-boxes', None, 3),
    ('inventory.items', 'Items Catalog', 'fa-cube', 'inventory', 1),
    ('inventory.categories', 'Categories', 'fa-tag', 'inventory', 2),
    ('inventory.suppliers', 'Suppliers', 'fa-truck', 'inventory', 3),
    ('inventory.purchase_orders', 'Purchase Orders', 'fa-receipt', 'inventory', 4),

    ('bus', 'School Buses', 'fa-bus-alt', None, 4),
    ('bus.fleet', 'Fleet', 'fa-bus', 'bus', 1),
    ('bus.students', 'Students', 'fa-users', 'bus', 2),
    ('bus.trips', 'Trips', 'fa-route', 'bus', 3),

    ('access_control', 'Access Control', 'fa-shield-alt', None, 5),
]

def seed():
    created_count = 0
    # Create parents first
    for data in sections_data:
        if data[3] is None:
            obj, created = Section.objects.get_or_create(
                codename=data[0],
                defaults={'name': data[1], 'icon': data[2], 'order': data[4]}
            )
            if created:
                created_count += 1
    
    # Create children
    for data in sections_data:
        if data[3] is not None:
            parent = Section.objects.get(codename=data[3])
            obj, created = Section.objects.get_or_create(
                codename=data[0],
                defaults={'name': data[1], 'icon': data[2], 'parent': parent, 'order': data[4]}
            )
            if created:
                created_count += 1
                
    print(f"Seeded {created_count} sections.")

seed()

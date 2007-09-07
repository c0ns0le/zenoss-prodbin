###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################


import Migrate

class RemoveZenPackMenuItem(Migrate.Step):
    version = Migrate.Version(2, 1, 0)
    
    def cutover(self, dmd):
        
        items = dmd.zenMenus.ZenPack_list.zenMenuItems
        if hasattr(items, 'removeZenPack'):        
            dmd.zenMenus.ZenPack_list.zenMenuItems._delObject('removeZenPack')


RemoveZenPackMenuItem()

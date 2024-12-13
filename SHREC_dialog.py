# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SHRECDialog
                                 A QGIS plugin
 Plugin pour controller les géométries
                             -------------------
        begin                : 2024-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Ta'o D
        email                : ta-o.darbellay@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
import base64
from qgis.PyQt.QtWidgets import QLabel, QGridLayout
from qgis.PyQt.QtGui import QPixmap

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/SHREC_dialog_base.ui'))


class SHREC_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SHREC_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_couches.ui'))
class choix_couche(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_couche, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_controles.ui'))
class choix_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/voir_controles.ui'))
class voir_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(voir_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/pas_controles.ui'))
class pas_controles(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(pas_controles, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/dialog.ui'))
class dialog(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(dialog, self).__init__(parent)
        self.setupUi(self)
        base64_data = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+j610wsqjZ1A4OR6+1bsGnZOdpzkYxyR1GeOO+Ov9a6O10/8AdpgH5QMkMRk9fp+h/nW3bab3xjjIOOByR+Q6evHWvzGrDX3lZvbutr7rrY+kpTbV5WbT3WnMlZ3t01dvkYFvpa5BxngnHoCeFwQMAAgZBxW3Dp6orM6jCAsXfaFVcZJJIwAO5yOhz0xXS2+lggNg4A6YI5B6gc56HBxk/pXgHxL8Q32v3t14S8NtJ9jtZGg1S6h+Q3d0nyvaK+0t9mgk3RS7QDPcK4CtDHHJN4WaY+GW0JV60XLXlpU4/FUnZOy2dusn0R9Rw7keM4hzGngcIlHmSnXryv7PD0bx5pz7vW0I6Ob0utzP8Z/GfQdCkuLDQLKTxFqcRkQzRsINJhZd8e4ThJJb0RyIMLbRxwXEZzFf9N3z9qv7RvxFt3Z4dO0C1VQMwDT7hgwxjDPcX08gbnohUtglR8uK9m8N/CmN9s16c7hvlLPGGj3HBdlwWHIIOfuhXIJKlRheLvhVZwJNJHGZwSGVgoxhCMI2UCMQpwrbXkKjIJ6H85r5/m2Icqqn7GnzO1Ololdq176ya6u/yXT+i8s8OuFsFQ9hWpLG4qMV7StiHKU5TVrtRSjThvpGEVZWTcrtvzPw9+2MUvlsfGnhSJI8iNr/AEOSSGSMDI8w2N7POt0znoq3dkqlWyTnbX1f4X8c+EvH2nNqPhTV7fUFQL9rt2zb6hYSOu5YruylAmhJ+YLKA1tO0cpt5pVRiPz5+IHwwtlgneKMR3QQFGiYZOeV6EbSOjjJyuAVwQtfIOk+PfFfwx8SC/0zV7ixu7e5320ltICsqByjJLG26CaN4zskgnSWKVC0ciPG7I3fl2dVpcscRyzimuaWkZct4py0stG3dWWmt+r+V4i4Ew2HUquWp0Hq401zuk7a8rUruN9o8j02aZ+6NwhAbJByT+ALDgfke/asadoV6n3IBA74HbPrzXk/wm+Ltv8AFDwtFqjeVb6vZmO21i1gJ8tLgqTHcxK7M6QXYSRkicl4ZI5oi0kaxTzejGRXPBJ6DPTJye/r+VffYShCpSjUhJSp1EpqSd29lsvRp3elj8ixUp4WtOlXg4VKc3GUW17rVu6WjumvLcc4RvuDK+vofTP5enWhIic7cZ25BzznPf8A+t3FPjt2OMYwCecjI/DGfTt0q7DCy5ynT5egP8vxznFdLw3Zpvtt2V9vJ9ev388cbGWie/V2tfT077q616s9fsrQrGvTGMkYOOwwevp7ZzntXUWlkpGOoPK/p3YE5GPWq1lASkY6liBgZHTqpyD6+/JNdXZ24yDyeOx/IcjGOvOfYn09vF0ZJ33sulktba62b1bV/I+Po1bpJXbV+1+vn+f/AA/K+NdQbw34R1jVolxdRWqwWTAgFby8kjtYHUYO8wPMLgr/ABJE3pg+DfDjSbJY2u7keZLIxYqmPOkUHYWGd+fnwrPywGcMoJLe8fF6wafwHcSKrBLXULC5nwpOYzK9spfAI2+bcw854PIGcV4N4c+IXw48MaTJe+I/FOgaDa2kwt7ufVdQtdPtku/JFx9nSe6dIZboxMJBbxPJM5OGiYsNv5nxPz1MzwtKSTpQo8yjJaKUpe9Lbe0Vr06Wuf0H4WU6NPJcxxUE5YipilTnKFlVUYUYOEE9WrOpJ37z21PV5102wlmnigggnvAv2mVYY1dxBGViMkmxQ5iXEcYlYgDiPdtkxg6iA2QrCWJUeQOYwQSpBVRgg4JYLjIUjhujBrumeMfhp47t7W40PXbPU7LUAJLK7s3lMUzQPEsirIY40jlZrmECGRopXEqOqMjKxfret+HvDFleGZlmWBUMcKAyTPvkKIIw3JyQxLEgFFd94VGI8eeDgk5OpSUFb4VrstLaWb6WbufpuExDXIlQxUq7XvRnCy5XyxUvaX+ztql06nyT8XLGRLC9lt7YpNOrkEKdu1d6I4AHG4u/PBJbDgEV+VPxe0UQXVhdJ+6MmprBdYTaSZpABkdFVXKBdgG5d2/ocfZXx+/4KEfszeCdRuPDeveJ9Zj1qGYwS2ll4bvdYhhlVZNiPeaWlzBGJcP87oY1eKSM/vkUL+dPxf8A2m/hp48jZ/C808VvP9hvdNlvLSSymmCSo7x3FhKr3OnTW7mNG+0RwqrEKo2qyp531SpGSqQTcJvSduVWsrpLe7u3bsru1rnTmeKw2Iw/s3OCr0ouM4ResWlHWel7pqzs76v0f0Z+z148l8KfEK605rjZp2r2MlvOjOdomijFzbHacKC0sXljOSis/Te2f0V0fxtaX2FjuEY7hkBxjJ9QMke3T6kV+IvgzxE81zca5FON0cMd2jkn5V8pUYqfvBj3zjJZicY2j0zwh8b9Sg1AQrdv9/g+YWxgrgnOM8cYA+lfpXDEp1MH7N2tCfLre9ppO33xk1fo18v5x40oxp5h7RKzqQ9+2zcZN9l9lxSu9reV/wBtrDVBKq/N9dpB5IyR6YDcdR25Oa6+yKykDOQxGR68H6deD9K/PbwJ8aL2RIPtgMqEr86577eoxycHvnr0xX2F4K8cWWqpGPM2ucZViMgBSQcYxjJ7HOQccc19G6DV21ra+nZ20sr2s+n/AAD4bnad72V9L7en9eZ9nWMOEV8DPXB6YOMdR7cHI5HPYV1FlECFwCPmyR/s4x24x/nPY5FmnyIozgDOP55xjPOe3f2rprRcYx0BBx9ck19Fi6DdpJWaWuvpb13fS+y8j5+hUtZp6vr/AJrz6/1bjfi1qGl2Xw/8QWN/ffY7zWdLv7PRES3uLma41eK3a8sAkVrb3DRpHdwW5mupljs7YMjXU0UbAt/PF418C+Ffhlo/i/8A4S34OeOPjz8TfB/h/SPGPiWPUfiv4s+HPhGwn8SeI9H0yKx0/WtIsNe1HWdbtYdak1/xDYaX4a1iDQ/AmnaprWuX8McKQal+4v7TvhabWH+EGtExSWPh/wCIDG7glDMfN1fRr20sJ0j3pE7W93EjK0pfymKyxxNIikc/psttpU09wmk2Gpz30my7F1b2rkM8YhL4NjPEVEKxxHMW4xRxlzKSC35Xn1ap/bSjUowVGjShDmu/aVIShGV0ltapNxsk5Wg11P6f8OcjpS4QoYvAYudbH5qsZWxFB+yVPBYnDY6rhKUI87s/aYbDwrVPaverHl7HwB+wB8UtL+Inw78J64nwAvvgadcgv9bg8JT+NLnxrJpqaTqFzaP/AG1PrGi+HdU0rUbuWR57eVtKit7+OV2trqaSJUPXft7fHSH4cyeCtM8MQpcX3irWLGwu445gsotncJM4fduEiQlhCzYzKyqQq7mX7G/sqDSYtU1aw01ILzVDJG5EigSPKVfesUCRxRbWBZxHBGZVhJdCCgX8Tf8AgoZcXej+J/B3i/UbpJvDmm38a3EmJlSDLpJ5024gIqyKxeSPYIxn5dpNfF4mDbnBXcJ1FLVSXKo2933rN/0mj9hyvJoVaM8TUxUlPB0HRbVl7WpU5FOUqcJSgvZTS05ne0ne+i+0/E1l8Ym+EXxA8d/syeDPhN4e+JfhzQZJPhl4a1j4eaB4z1f4naq99p9nDrGs+LNS8TeGY/DejSWQu5nkmv49Vi0i9j1mW2kvNGj8F67+VvjCL9pP466l4W8M/tT+AvBFl461N1vrvW/APh650J/DN5Frv2Gfw8RJqfiWyvIpvD4g1WPXbPU54p9Sv3ga3srTQYG1/wDYP9jTx/8A8JH8NtOn08m4MdqxhDTk5hLGWJ7R0kXdbtIZoriMBoXZvPi8s3HPT/FS905Zp5Z9JtzetGx+0yBV8qRHKruLp87fL5kUiSK6fKjo22UV6E61KGBoqnTUqtNNSnJTUuZzi7vWztflUY6Ri7WT1fkw4YxWJx+NqwrTlRqUVL2TrUZUqcYRgpSguRVuWTi5OU5zl7Rtc1kor8DPGumXfwhsvEmgi8jP9mSlIdSvzsibTIbhA9zciNoTGpgk86ZEMbBVAVlchq4f4YeIl8QaVZ6+dPn0i5h1m60q9sriVZGxCQbS9VRkwC9VZ91tvm+zS208Kz3MaR3D6P8AwUD1HzrG/wBOtdYl0q413X/CHh6LWrYxJJYC91zSxdX0gkSZZI7a1jubmSB4ZRcoJLd1CysF8k+DWs63d/D3w/qPiC3ex1rVotEudYtygj26jYeHtLs7w7E/dq0179supli2oJ7iTCgnbXvcOV66xWHjGco0p8zqU7+5Jxpybv2aet12W19PieKcoyOXDXFNfEYeEszwDy1YDExbVSjOriaFKVK97ThXpOaqJ3+GLSXxH6r/AA5ulurKPDBjhe/PAGMe3XOc/wA6+tfAd/Jb3EeG2sMdT1Gfp15JwcdDlq+Dfgrqck8KRlz820A47ZUEAYHPHXtz619t+E3xewITkErntuyDkfoeBX6QlzQ5vTS3e3+Z/M9XmUmrySu1ZbO0tbp+Vtu6P2gtB8qY47Dg+pz1rpLT+EA45OQRxgdgfU1z1s/C5ABHIy36AYHvmt21l+6CB97OcYA69D+XH1r6bEUrdl2au39laael+3zZ8lSratXtZLTrrq9Lanh37V1xLp/wktdWjtzMukfEr4V6hcytO0EVlp3/AAn2gWuq3kzD5XSPTLm6RIpGSOSaWJWdDg1xltdWdjZ3Wp3wPkBGmZwAFKqygsm7Ay4C7NvO3aeCor1r9ozwtfeOfgB8YfCmmxefqmsfDjxfaaTGX2Z1dtCvW0qVH2tslt9RW2nhlALRyxI6KHVSPyFuP2hNf+Pn7HPiXVvhtrGneG/iTp9joOnXd/qV5b2dvpn2600i/wBY1Oa68u4NokOn3k0wmW2mktcLcyCxVjPb/kPHMZYHFUMUlGXtcO1qmlzUpKLvK1tqkW9LJaWbuf0r4M5vTnlmMyypzqNHFRm5wqPmlCulUUVFv3daU1o0m5cz1Tv96at8RrbT5vCrTXPgyBtW1e5t7bT/ABD4kttJlt4Y1hdDbWb208ep6pcO1uv9nzT6d5ENyvnXStL5cn5gf8FBvEHizxJqnhewv/hFo2mfDDTtVl0vxx4s8T64fCllb2Nw0vnXugQW2i6pN4s1y1t7ae5g0OBtItWSZXn14nbZH5x+H/7At94mttB8e/GX4/fErxd4imi1C+8N3fhrwbqupaBpFxfX04up7C3vdV1awmtruGdYnvb23S5WOJJXaKz1C5ju+t+Kn7Kuq+IfAOseDfiz+0h4n8f6Xa2Nnb+Fbe2+G/iO2vtB0uC88R3moS6rps3i3VLS+1fUTe6XYm6hWS6Om6N9njtZJNQN9b/FqpiqtBy9lKUJOMk4OLUmkk5JNX0d5QsrX0Z/QGAwmMrezr4DLKs41YzjGSU0pQlJz95RmoNO/s3JrmTbndzk7fRf/BNTRrPwjp3xI06Hxdp+seB9R8Sm++F1ubm2e5XQ1tLePUWVUu742tveaqlzqNppc8hvLSC5f7RDaPI1vD9I/tGxiPRNSmtg8EqRyyidEGECM7s7DKeaZUAWMF/vSE4OzI/mJ8Nfs0/tF/Djxatt+zH+0t4osn0zVpLmz8N+JfDHxC8GaLDI9tcmLTBqWv2A8GTW7Za1RdR1q6ltYYrVbKRIFaG4/aGH9pXxA37Nkdp8cp9LT4weHYtX8OarPbT6Xaw+LdQ0iSSBZ9OMNybCSQhJIr64guWhhW1mvSoiDq/JVnKLp0It1HUlH3XFwqQu4fGrWeq3jtZ3snc4YZ1UwVbHfWcNVwdaFGdOUFOPJdOz9mlrvJ6Nbbu+h+E37cni7Utd1HwZ4I04S3viDVfiXp5trFEiDXun2E17siBupIYFSeIRSlp5oYYYYpJNzQwvu9p8Hx3sOheHdP1CJ4b+3sYFvY2aOQx3cuXnUGF3j3BsswWRwHLYYrXwrpnjHW/jP+1wmswFJPDfh5ta1SeNYw0lklrb3lno08xmmM0Zu/tVi6pEuyK58x+sDGL9DfDcJudWhVhkBwTzgD5sHOfUE+/Hr1/RMhwMYQhW19pZqKb0Tmoxl0V76q6v5n89cTcUYqtHH5ao0vq+MxdHE15Si3WbwjmqVKMlNwhBuUZzXJzppK6V0fbfwW04wxWz4GT8w6kY2gjByTn1B6c19qeF1Zr+DacAMM5z1x6YHYn26/Svl74Y2qW1lFIAV+UEc4xlRx35PUc4Az7Y+nvB8+b2JsjO8DB7Yz0z/jx9K+2jFxpJWd7Lv/d8vNL+mfldSanV8k5ff7q3/wC3b26t76H7XRrkJ0JHU888cj88kdetaEEqgjrxjGPrn2rJyyj5uOnTk8dyMZAH+eMkKLgpksy9QeeeBjvj1P4V91iKFpKPK76We62ireq9eq+X5zHERv1Vuqd+i6dOqtt+vWo8c8EsMw3QTRNDKD/zzkUq4IGD9wkHB9cHPNfxgfH/AOMel/sgftQftufAb4Z+LNKuNCudITUdD0vTZTeWugWXjGDw+mr+Ep7Gzt3htdZ8If29baVp9qJhMNA1HRblJob2ytyn9aPxN+Itp4L8G69q/wButra/j0y8i0hJpIwbjWJoHj0+KKF3Q3D/AGgrI8K7iY45CcKCR/FP+0N+wPL8Qv8Ago5F8QvEHxA1Lwf8Mv2l/DN5oWkeK5RJc6f4U/aO8PeEING8K6f4gkK28lxoHieHRLFtPtIL+C517VoH0VJLa4Wwkb5jijhmOOyPEY6vSl7PB1FLmVNylGFv3rXL7zpqSgpJJ2et0r2/QvD/ADnF4LN40sHO8sZBUPZymoRnLeLk6lopwXMldq/M0r3sf00eF/iPbeMPgP4R8a/Bfxppuk6je+H9C1G60i8hsddtlutU02C4ewVbm6mgNqXe8vl1K0Vo47S21C7uLmK4jnntvz1+LX7Qv7aELWkcY8OW0Q1J7SN9Z+HiRaJqmkR7YjImpC0i+0Xtjd3tmt3Z6KtzdNYSARi2dVaT8xPhh8QPi7+yR8QNb/Z3/aGe98Ga74ansW0Sx1W+t7D4datbaGuhwwa74XvJrO0j8RWGtafpdzcWN7pqW0hT7RpniC30y41TW0H2R+0Z+11dX/hS4jvbPwxrdhpN5pt5YTaZFL5t5q2rxeH7WW0eNLzGovqNlBcXen3lsUK2d0NOUQW9pK15+B1cvq4at7P2mIdKbSo+wny0JRdrTjb3Xo9bNpPoj+rcuz7DVcJ7d1HSxNL3al5uFei1GKcJqMua3utq71vu7q9j4y/HxfgR4Kuvij4t16x8YeKPEfhW9W20rRf7LfQt+o2Fsq6NefZ9U+32ttPBPNAt19khiurmGaEMJYZ5Lb+ab4gft4eItd+G914Lupre30jQte1ZNA/4+dUu1/te91KSaGDUZHurq/tvMHlQzS3im701pbO3jk2R3jUf2tfjlPr3iw6Ho1/r/iO81aO5tbDw1ZNqF9qUP2qYRrpcDWcNtDeXk81pDqMMn2SB7eGSDTrW1v2iYxe3/sT/APBMfxpqmoaT8Yfj5YGztbRl1zQPAjWixWtreoRcWureIAUe2E6DDR6WDJ9nuI1uLqaeZjAPpMFlGCy7CPF5lPmnUlGpRpy1r1nbSEE27atc07JRV38W/wCdZvxBmWdZjPCZUpezpc1KpUT/AHUFzwTq1JOK5pWXNGLk5bK/VVv2O/HWi/DXxovw3+Jem6xpvxW+NHgnTviR4e1G9Qraw+DtNvvEum6Z4WurXAOm6qiaVqfiLUJWK+dPqn2S5XzrJru6/T7wrq8aaxG6thHkX5iN3O7uMnJO7qOnX0FfI3xA8AeFde/aB1H4hyz2enTfD/wTqPwl8EuzwqupeIdX2a1rkqtMQWi0TTZorNniLeVP4jnSOGaf92ev8E/ErTZb0aVez3Frqump5ksk9vOLa7hgeSJ7qC7BliZsxSNNHK8U65aYoYczV9/g8ur18ry/M6GFqxVeKdSlGm3GMVfknFRs3ScVF/De7u3Y/MM1q0sNmuPy+WIVX6vUcYVJN++5Qh7SM76KaqcylaTTtZPQ/ZnwBrkUulx8qWCrxnOTxj16gZx2zjPFfS3gW6ElwjM3Vxg44B5x7jgkZxgHmvyy8DfEkW1pCq3IdGVcMsnyuhXKOpViNrjpt9vevtL4XfE3Ti8AuLlI2B5LOfxGOeOeSD9Cc8+hFprltrGycWrNOy6Ptte1ro8acGm7q6evlZ7fnp/w9v3p+I3xr+F/wttpJ/HPjrw7oEqRmT+z7rUYJNYmQg4a30i3M+pTrgEF0tDGpBDOOtfm58WP+Cj9nJJe6V8KdFEiIpCeKfEPkqr58wM+n6EswkKLtR472/mfY6mKfSWyqyfjNf3mp6/dyyas17qNzMzQzLI5mhkln8zYIlEkokPmbIxdwIrowjcmeNDG3c6Z4fmWWC2eMLp/F3JMt5vMifIEZTLPpfnRRO/li2aBoQXSMQyNhp/3ejk2EpTUqqliHG1ozdqd9NeRb7bSlJb6H5dD3Xa7k9k+jv3V+nrpqes3fxF8d/E74z/DvXfGfi691IWN3qF5dQahqQj0+CfxLp114U0WFEEdpp2h2dnNfXuoT25tobVZJbadi9xbo0Fz9o6w0jVPhR8ZdC8U+IdN8IW7eEJtA0nUdVv49Kk0/wAZX2qaePCUVveyNA0OvL4pSwh0GCKQagfEl1YwaUn9pvbRy+a31ju+13t7E0cMpmijubRmWWKG2Mv2X7ULO/nvWWMSM0EUgj8lWe7SHylczfIH/BQ3Q/iB8eP2Yh4B8DaprsfxY8LfFH4XeOPh1qtjf3GlXniltK8Qf2aPDPiTVoHFwll4Vt9VXxR4b1y7I+w3Oj6RZ3t8H0vQjbehiqUJ4SrS9iqlOWHnT9jTUY3U48toqyj8LelteulzuwdaWHqwmpWnCpCcJttWlFxcfPdbJt2P0v8A+Cd37Q/7Nf8AwVy+Dc/7MP7dHw98La7+1J+z95nhfxGdcZtL8W6jJpk8FhH4/wDBuv6dLYa5pd3qkum2NzrP9mXC2hv0W6eGWxvo4q9/8Z/8G8H7JOs20trpXj/9obSdF8prc6JB8QtK1LTZLZjfbYoZNR8M3moW4hF9JBbeVeMtraD7OkQ/dzx/x6ePfjBF8Jbj9nr42eDrbxZ4E/aAsYLvV9a+PHg260nQb3WJtEkt9C1nw58SPCk88txrHjPwfqumXfhfxhp2q3umTa/qcWpa7PqVtY6raaJpv91H/BIz/gozpn7dHwgjtPE1xpbfFbwZaWsHin+xvtA0jX7dN0Nv4p0SC+jt723tb1oSLvTry1tb7Tb0T2d5bRTL5Mf8z8ZcEZnw3VjiYKpHLMTUk8JWpSboxbtJQnZyVOo/eahJLm5Xyt8rt+98N8VYLiGjKnanVx+Gpwni6FRctaUPdi5p3jKpBNqMpJSUeaKklzLm+cPg7/wRN/Zi+Ad4l54B8C3+q6+qG0k8Y+N9SuvEXifyV3GT7Nd3Yh07S0nhdo5k0PS9PWfMouA+4GvVvjv8CtI8JeD77RdHjt7AnTGilmSMRxQwbCs78BMKFjfODnkhWG5i37N+O/FXhT4deC/EvxC8TzeTo/hjR7vVdQyEaeSO3ULBZ2NuWjE+oahdGCysYWYNPeXUMCOhkTH8tX7VX7c3xM8fWWsT6RocHhCafUNGm0+1NrfaxIbWy1HTbqxsfskUUMfiLUde1iA29voNjqkEetaSV0u+WfTNZvmXw8g4FzbinE+1jNrC0a1GOLxVas+eMPdcoUYVHJ1avJpyQXLDmg5+7Kx6uY8a5XkGFq044VU8U6E/qeHp0klOppDmnJRiqcFLeo/eqLmSvJM/L79rnwt4c8O6b4X8G+HF8/xHpd5f64+s2TH+0L7WtRuZ7zxFDJcI1tOY2EcI8nMrNHY2qlYHgbzPDvBekyX97ZCXTksdf0Kw8OS68WHmG6g8Sz6nqSalJ50W6K7WynsEltxMbky6fNdA28c9wg+vvH/gyy1HxXo/xC8VLe6H4Hl8Paf46mhuJbS/u9LtNU05bvXfDkVxDazw+INc8OaxFqXhZZtPhWC+vtJvNQaGHRrO48ji/hvaXF9Z6/4s1y0n0vUPiLrdzrkemR2Ecw0/QBFFpPh/So3vhcW9j/ZXhux0+KaJpytzdTuFuJiqNN/R2WZVSoRpYWjFwoYenCnFS15VRUIRu0l73KtWlG/Y/AcfmNTEzniKkuapXqyq1Gr2lOo+aXfq9Pv6HW6T4OjRZobS7txLNK9y7Wty7Qb5PJmlCQ24aeyljgmjvLmJ54ImYtHERFLHPN6XY6Dr2mRQtZ6t58mII4oprZo281okPzypMkqMqrJJMxhfY7xx8gSSDZtoWljghig06506KeUJHdwxRfZ/MSIJbWM1ncRx3EcayM0qQubV0CGFxIskddjpEtnOl3FLHaLLCY7Zlhs5hLaEQvArR5hiVC8MIYNYWupRySFcTzvGqP3YjIstxCtiMNTqNtPm5UpxaSvy1ElOz9beVzHD5ji6b92q4xS20aXwxV1O6aSXa9z/2Q=="
        self.im = QPixmap()
        self.im.loadFromData(base64.b64decode(base64_data))
        self.label = QLabel()
        self.label.setPixmap(self.im)

        self.grid = QGridLayout()
        self.grid.addWidget(self.label,2,2)
        self.setLayout(self.grid)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/trop_de_couches.ui'))
class trop_de_couches(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(trop_de_couches, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/choix_precis.ui'))
class choix_precis(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(choix_precis, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

FORM_CLASS1, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'ui/lancer.ui'))
class lancer(QtWidgets.QDialog, FORM_CLASS1):

    def __init__(self, parent=None):
        """Constructor."""
        super(lancer, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
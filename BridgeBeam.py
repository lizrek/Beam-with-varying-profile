import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate

from StdReinfShapeBuilder.RotationAngles import RotationAngles
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from HandleService import HandleService

HOLERADIUS = 45.5
TOPSHHEIGHT = 320.0
BOTSHUPHEIGHT = 160.0
BOTSHLOWHEIGHT = 153.0
RIBHEIGHT = 467.0
RECTANGULARHOLE = 100.0
DIFFERENCE = 20.0


def check_allplan_version(build_ele, version):
    # Delete unused arguments
    del build_ele
    del version

    # Support all versions
    return True


def create_element(build_ele, doc):
    # Create Element
    element = BridgeBeam(doc)

    # Return a tuple with elements list and handles list
    return element.create(build_ele)


def move_handle(build_ele, handle_prop, input_pnt, doc):
    # Change the handle properties
    build_ele.change_property(handle_prop, input_pnt)

    if handle_prop.handle_id == "BeamHeight":
        build_ele.RibHeight.value = (
            build_ele.BeamHeight.value
            - build_ele.TopShHeight.value
            - build_ele.BotShLowHeight.value
            - build_ele.BotShUpHeight.value
        )
        hole_height = (
            build_ele.BeamHeight.value - build_ele.TopShHeight.value - HOLERADIUS
        )
        if build_ele.HoleHeight.value > hole_height:
            build_ele.HoleHeight.value = hole_height
    elif (
        (handle_prop.handle_id == "TopShWidth")
        or (handle_prop.handle_id == "BotShWidth")
        or (handle_prop.handle_id == "RibThick")
    ):
        min_sh_width = min(build_ele.TopShWidth.value, build_ele.BotShWidth.value) - RECTANGULARHOLE
        if (build_ele.RibThick.value >= min_sh_width):
            build_ele.RibThick.value = min_sh_width
        if (build_ele.RibThick.value <= build_ele.VaryingRibThick.value):
            build_ele.VaryingRibThick.value = build_ele.RibThick.value - DIFFERENCE
        elif (
            build_ele.RibThick.value - RECTANGULARHOLE
            >= build_ele.VaryingRibThick.value
        ):
            build_ele.VaryingRibThick.value = build_ele.RibThick.value - RECTANGULARHOLE

    # Recreate element with new properties
    return create_element(build_ele, doc)


def modify_element_property(build_ele, name, value):
    # Handle dependencies for changed property
    # Return true/false for palette refresh
    if name == "BeamHeight":
        change = (
            value
            - build_ele.TopShHeight.value
            - build_ele.RibHeight.value
            - build_ele.BotShUpHeight.value
            - build_ele.BotShLowHeight.value
        )
        #print(change)
        if change < 0:
            change = abs(change)
            if build_ele.TopShHeight.value > TOPSHHEIGHT:
                if build_ele.TopShHeight.value - change < TOPSHHEIGHT:
                    change -= build_ele.TopShHeight.value - TOPSHHEIGHT
                    build_ele.TopShHeight.value = TOPSHHEIGHT
                else:
                    build_ele.TopShHeight.value -= change
                    change = 0.0
            if (change != 0) and (build_ele.BotShUpHeight.value > BOTSHUPHEIGHT):
                if build_ele.BotShUpHeight.value - change < BOTSHUPHEIGHT:
                    change -= build_ele.BotShUpHeight.value - BOTSHUPHEIGHT
                    build_ele.BotShUpHeight.value = BOTSHUPHEIGHT
                else:
                    build_ele.BotShUpHeight.value -= change
                    change = 0.0
            if (change != 0) and (build_ele.BotShLowHeight.value > BOTSHLOWHEIGHT):
                if build_ele.BotShLowHeight.value - change < BOTSHLOWHEIGHT:
                    change -= build_ele.BotShLowHeight.value - BOTSHLOWHEIGHT
                    build_ele.BotShLowHeight.value = BOTSHLOWHEIGHT
                else:
                    build_ele.BotShLowHeight.value -= change
                    change = 0.0
            if (change != 0) and (build_ele.RibHeight.value > RIBHEIGHT):
                if build_ele.RibHeight.value - change < RIBHEIGHT:
                    change -= build_ele.RibHeight.value - RIBHEIGHT
                    build_ele.RibHeight.value = RIBHEIGHT
                else:
                    build_ele.RibHeight.value -= change
                    change = 0.0
        else:
            build_ele.RibHeight.value += change
        hole_height_from_top = value - build_ele.TopShHeight.value - HOLERADIUS
        if hole_height_from_top < build_ele.HoleHeight.value:
            build_ele.HoleHeight.value = hole_height_from_top
    else:
        if name == "TopShHeight":
            build_ele.BeamHeight.value = (
                value
                + build_ele.RibHeight.value
                + build_ele.BotShUpHeight.value
                + build_ele.BotShLowHeight.value
            )
        if name == "RibHeight":
            build_ele.BeamHeight.value = (
                value
                + build_ele.TopShHeight.value
                + build_ele.BotShUpHeight.value
                + build_ele.BotShLowHeight.value
            )
        if name == "BotShUpHeight":
            build_ele.BeamHeight.value = (
                value
                + build_ele.TopShHeight.value
                + build_ele.RibHeight.value
                + build_ele.BotShLowHeight.value
            )
            hole_height_from_bot = value + build_ele.BotShLowHeight.value + HOLERADIUS
            if hole_height_from_bot > build_ele.HoleHeight.value:
                build_ele.HoleHeight.value = hole_height_from_bot
        if name == "BotShLowHeight":
            build_ele.BeamHeight.value = (
                value
                + build_ele.TopShHeight.value
                + build_ele.RibHeight.value
                + build_ele.BotShUpHeight.value
            )
            hole_height_from_bot = build_ele.BotShUpHeight.value + value + HOLERADIUS
            if hole_height_from_bot > build_ele.HoleHeight.value:
                build_ele.HoleHeight.value = hole_height_from_bot
        if name == "HoleHeight":
            hole_height_from_top = (
                build_ele.BeamHeight.value - build_ele.TopShHeight.value - HOLERADIUS
            )
            hole_height_from_bot = (
                build_ele.BotShLowHeight.value
                + build_ele.BotShUpHeight.value
                + HOLERADIUS
            )
            if value > hole_height_from_top:
                build_ele.HoleHeight.value = hole_height_from_top
            elif value < hole_height_from_bot:
                build_ele.HoleHeight.value = hole_height_from_bot
        if (name == "HoleDepth") and (value >= build_ele.BeamLength.value / 2.0):
            build_ele.HoleDepth.value = build_ele.BeamLength.value / 2.0 - HOLERADIUS
        if (name == "TopShWidth") or (name == "BotShWidth") or (name == "RibThick"):
            min_sh_width = (
                min(build_ele.TopShWidth.value, build_ele.BotShWidth.value)
                - RECTANGULARHOLE
            )
            if build_ele.RibThick.value >= min_sh_width:
                build_ele.RibThick.value = min_sh_width
            if value <= build_ele.VaryingRibThick.value:
                build_ele.VaryingRibThick.value = build_ele.RibThick.value - DIFFERENCE
            elif value - RECTANGULARHOLE >= build_ele.VaryingRibThick.value:
                build_ele.VaryingRibThick.value = (
                    build_ele.RibThick.value - RECTANGULARHOLE
                )
        if name == "VaryingStart":
            half_length = build_ele.BeamLength.value / 2.0
            if value >= half_length:
                build_ele.VaryingStart.value = half_length - 200.0
            half_length -= build_ele.VaryingStart.value
            if build_ele.VaryingLength.value >= half_length:
                build_ele.VaryingLength.value = half_length - RECTANGULARHOLE
        if name == "VaryingLength":
            half_lenght_from_start = (
                build_ele.BeamLength.value / 2.0 - build_ele.VaryingStart.value
            )
            if value >= half_lenght_from_start:
                build_ele.VaryingLength.value = half_lenght_from_start - RECTANGULARHOLE
        if name == "VaryingRibThick":
            varying_ribthick = build_ele.RibThick.value - DIFFERENCE
            if value >= build_ele.RibThick.value:
                build_ele.VaryingRibThick.value = varying_ribthick
            elif value <= varying_ribthick:
                build_ele.VaryingRibThick.value = varying_ribthick
    return True


class BridgeBeam:
    def __init__(self, doc):

        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):

        self._top_sh_width = build_ele.TopShWidth.value
        self._top_sh_height = build_ele.TopShHeight.value

        self._bot_sh_width = build_ele.BotShWidth.value
        self._bot_sh_up_height = build_ele.BotShUpHeight.value
        self._bot_sh_low_height = build_ele.BotShLowHeight.value
        self._bot_sh_height = self._bot_sh_up_height + self._bot_sh_low_height

        self._rib_thickness = build_ele.RibThick.value
        self._rib_height = build_ele.RibHeight.value

        self._varying_start = build_ele.VaryingStart.value
        self._varying_length = build_ele.VaryingLength.value
        self._varying_end = self._varying_start + self._varying_length
        self._varying_rib_thickness = build_ele.VaryingRibThick.value

        self._beam_length = build_ele.BeamLength.value
        self._beam_width = max(self._top_sh_width, self._bot_sh_width)
        self._beam_height = build_ele.BeamHeight.value

        self._hole_depth = build_ele.HoleDepth.value
        self._hole_height = build_ele.HoleHeight.value

        self._angleX = build_ele.RotationAngleX.value
        self._angleY = build_ele.RotationAngleY.value
        self._angleZ = build_ele.RotationAngleZ.value

        self.create_beam(build_ele)
        self.create_handles(build_ele)

        AllplanBaseElements.ElementTransform(
            AllplanGeo.Vector3D(),
            self._angleX,
            self._angleY,
            self._angleZ,
            self.model_ele_list,
        )

        rotation_angles = RotationAngles(self._angleX, self._angleY, self._angleZ)
        HandleService.transform_handles(
            self.handle_list, rotation_angles.get_rotation_matrix()
        )

        return (self.model_ele_list, self.handle_list)

    def create_beam(self, build_ele):
        common_properties = AllplanBaseElements.CommonProperties()
        common_properties.GetGlobalProperties()
        common_properties.Pen = 1
        common_properties.Color = build_ele.Color3.value
        common_properties.Stroke = 1

        breps = AllplanGeo.BRep3DList()
        # bottom shelf
        bottom_shelf = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    (self._beam_width - self._bot_sh_width) / 2.0, 0.0, 0.0
                ),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            self._bot_sh_width / 2.0,
            self._beam_length / 2.0,
            self._bot_sh_height,
        )

        edges = AllplanUtil.VecSizeTList()
        edges.append(10)
        err, bottom_shelf = AllplanGeo.ChamferCalculus.Calculate(
            bottom_shelf, edges, DIFFERENCE, False
        )
        if not GeometryValidate.polyhedron(err):
            return
        breps.append(bottom_shelf)

        # top shelf
        top_shelf = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    (self._beam_width - self._top_sh_width) / 2.0,
                    0.0,
                    self._beam_height - self._top_sh_height,
                ),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            self._top_sh_width / 2.0,
            self._beam_length / 2.0,
            self._top_sh_height,
        )

        top_shelf_notch = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    (self._beam_width - self._top_sh_width) / 2.0,
                    0.0,
                    self._beam_height - 45.0,
                ),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            60.0,
            self._beam_length / 2.0,
            45.0,
        )
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        breps.append(top_shelf)

        # rib
        rib = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(0.0, 0.0, self._bot_sh_height),
                AllplanGeo.Vector3D(1, 0, 0),
                AllplanGeo.Vector3D(0, 0, 1),
            ),
            self._beam_width / 2.0,
            self._beam_length / 2.0,
            self._rib_height,
        )
        breps.append(rib)

        err, beam = AllplanGeo.MakeUnion(breps)
        if not GeometryValidate.polyhedron(err):
            return

        # notches
        breps = AllplanGeo.BRep3DList()
        notch_polyline = AllplanGeo.Polyline3D()
        start_point = AllplanGeo.Point3D(
            (self._beam_width - self._rib_thickness) / 2.0,
            0.0,
            self._beam_height - self._top_sh_height,
        )
        notch_polyline += start_point
        notch_polyline += AllplanGeo.Point3D(
            (self._beam_width - self._rib_thickness) / 2.0, 0.0, self._bot_sh_height
        )
        notch_polyline += AllplanGeo.Point3D(
            (self._beam_width - self._bot_sh_width) / 2.0, 0.0, self._bot_sh_low_height
        )
        notch_polyline += AllplanGeo.Point3D(-10.0, 0.0, self._bot_sh_low_height)
        notch_polyline += AllplanGeo.Point3D(-10.0, 0.0, self._beam_height - RECTANGULARHOLE)
        notch_polyline += AllplanGeo.Point3D(
            (self._beam_width - self._top_sh_width) / 2.0,
            0.0,
            self._beam_height - RECTANGULARHOLE,
        )
        notch_polyline += start_point
        if not GeometryValidate.is_valid(notch_polyline):
            return

        polyline = AllplanGeo.Polyline3D()
        polyline += AllplanGeo.Point3D(0, 0, 0)
        polyline += (
            AllplanGeo.Point3D(0, self._varying_start, 0)
            if build_ele.CheckBoxV.value
            else AllplanGeo.Point3D(0, self._beam_length / 2.0, 0)
        )

        err, notch = AllplanGeo.CreateSweptBRep3D(notch_polyline, polyline, False, None)
        if not GeometryValidate.polyhedron(err):
            return
        edges = AllplanUtil.VecSizeTList()
        edges.append(3)
        edges.append(1)
        err, notch = AllplanGeo.FilletCalculus3D.Calculate(
            notch, edges, RECTANGULARHOLE, False
        )
        if not GeometryValidate.polyhedron(err):
            return
        breps.append(notch)

        # varying profile notches
        if build_ele.CheckBoxV.value:
            profiles = []
            profiles.append(
                AllplanGeo.Move(
                    notch_polyline, AllplanGeo.Vector3D(0, self._varying_start, 0)
                )
            )

            lines = []
            lines.append(
                AllplanGeo.Line3D(notch_polyline.GetPoint(0), notch_polyline.GetPoint(5))
            )
            lines.append(
                AllplanGeo.Line3D(notch_polyline.GetPoint(1), notch_polyline.GetPoint(2))
            )
            lines.append(
                AllplanGeo.Move(
                    AllplanGeo.Line3D(notch_polyline.GetPoint(0), notch_polyline.GetPoint(1)),
                    AllplanGeo.Vector3D(
                        (self._rib_thickness - self._varying_rib_thickness) / 2.0, 0, 0
                    ),
                )
            )
            intersections = [None, None]
            b, intersections[0] = AllplanGeo.IntersectionCalculusEx(lines[0], lines[2])
            b, intersections[1] = AllplanGeo.IntersectionCalculusEx(lines[1], lines[2])

            notch_polyline = AllplanGeo.Polyline3D()
            start_point = AllplanGeo.Point3D(
                (self._beam_width - self._varying_rib_thickness) / 2.0,
                self._varying_end,
                intersections[0].Z,
            )
            notch_polyline += start_point
            notch_polyline += AllplanGeo.Point3D(
                (self._beam_width - self._varying_rib_thickness) / 2.0,
                self._varying_end,
                intersections[1].Z,
            )
            notch_polyline += AllplanGeo.Point3D(
                (self._beam_width - self._bot_sh_width) / 2.0,
                self._varying_end,
                self._bot_sh_low_height,
            )
            notch_polyline += AllplanGeo.Point3D(
                -10.0, self._varying_end, self._bot_sh_low_height
            )
            notch_polyline += AllplanGeo.Point3D(
                -10.0, self._varying_end, self._beam_height - RECTANGULARHOLE
            )
            notch_polyline += AllplanGeo.Point3D(
                (self._beam_width - self._top_sh_width) / 2.0,
                self._varying_end,
                self._beam_height - RECTANGULARHOLE,
            )
            notch_polyline += start_point
            if not GeometryValidate.is_valid(notch_polyline):
                return

            polyline = AllplanGeo.Polyline3D()
            polyline += AllplanGeo.Point3D(0, self._varying_end, 0)
            polyline += AllplanGeo.Point3D(0, self._beam_length / 2.0, 0)

            err, notch = AllplanGeo.CreateSweptBRep3D(notch_polyline, polyline, False, None)
            if not GeometryValidate.polyhedron(err):
                return
            err, notch = AllplanGeo.FilletCalculus3D.Calculate(
                notch, edges, RECTANGULARHOLE, False
            )
            if not GeometryValidate.polyhedron(err):
                return
            breps.append(notch)

            profiles.append(notch_polyline)
            polyline = AllplanGeo.Line3D(
                profiles[0].GetStartPoint(), profiles[1].GetStartPoint()
            )

            err, notch = AllplanGeo.CreateRailSweptBRep3D(
                profiles, [polyline], True, False, False
            )

            edges = AllplanUtil.VecSizeTList()
            edges.append(11)
            edges.append(9)
            err, notch = AllplanGeo.FilletCalculus3D.Calculate(
                notch, edges, RECTANGULARHOLE, False
            )
            if not GeometryValidate.polyhedron(err):
                return
            breps.append(notch)

        # sling_holes
        sling_holes = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(
                    0, build_ele.HoleDepth.value, build_ele.HoleHeight.value
                ),
                AllplanGeo.Vector3D(0, 0, 1),
                AllplanGeo.Vector3D(1, 0, 0),
            ),
            HOLERADIUS,
            self._beam_width,
        )
        breps.append(sling_holes)

        err, beam = AllplanGeo.MakeSubtraction(beam, breps)
        if not GeometryValidate.polyhedron(err):
            return

        # result beam
        plane = AllplanGeo.Plane3D(
            AllplanGeo.Point3D(self._beam_width / 2.0, 0, 0),
            AllplanGeo.Vector3D(1, 0, 0),
        )
        err, beam = AllplanGeo.MakeUnion(beam, AllplanGeo.Mirror(beam, plane))
        if not GeometryValidate.polyhedron(err):
            return
        plane.Set(
            AllplanGeo.Point3D(0, self._beam_length / 2.0, 0),
            AllplanGeo.Vector3D(0, 1, 0),
        )
        err, beam = AllplanGeo.MakeUnion(beam, AllplanGeo.Mirror(beam, plane))
        if not GeometryValidate.polyhedron(err):
            return
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(common_properties, beam))

    def create_handles(self, build_ele):
        # Define handles
        handle1 = HandleProperties(
            "BeamLength",
            AllplanGeo.Point3D(0.0, self._beam_length, 0.0),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamLength", HandleDirection.point_dir)],
            HandleDirection.point_dir,
            True,
        )
        self.handle_list.append(handle1)

        handle2 = HandleProperties(
            "BeamHeight",
            AllplanGeo.Point3D(0.0, 0.0, self._beam_height),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamHeight", HandleDirection.point_dir)],
            HandleDirection.point_dir,
            True,
        )
        self.handle_list.append(handle2)

        handle3 = HandleProperties(
            "TopShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._top_sh_width) / 2.0 + self._top_sh_width,
                0.0,
                self._beam_height - 45.0,
            ),
            AllplanGeo.Point3D(
                (self._beam_width - self._top_sh_width) / 2.0,
                0,
                self._beam_height - 45.0,
            ),
            [("TopShWidth", HandleDirection.point_dir)],
            HandleDirection.point_dir,
            True,
        )
        self.handle_list.append(handle3)

        handle4 = HandleProperties(
            "BotShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._bot_sh_width) / 2.0 + self._bot_sh_width,
                0.0,
                self._bot_sh_low_height,
            ),
            AllplanGeo.Point3D(
                (self._beam_width - self._bot_sh_width) / 2.0,
                0,
                self._bot_sh_low_height,
            ),
            [("BotShWidth", HandleDirection.point_dir)],
            HandleDirection.point_dir,
            True,
        )
        self.handle_list.append(handle4)

        handle5 = HandleProperties(
            "RibThick",
            AllplanGeo.Point3D(
                (self._beam_width - self._rib_thickness) / 2.0 + self._rib_thickness,
                0.0,
                self._beam_height / 2.0,
            ),
            AllplanGeo.Point3D(
                (self._beam_width - self._rib_thickness) / 2.0,
                0,
                self._beam_height / 2.0,
            ),
            [("RibThick", HandleDirection.point_dir)],
            HandleDirection.point_dir,
            True,
        )
        self.handle_list.append(handle5)

from pymodaq_plugins_pylablib_camera.daq_viewer_plugins.plugins_2D.daq_2Dviewer_GenericPylablibCamera import DAQ_2DViewer_GenericPylablibCamera
from pymodaq.control_modules.viewer_utility_classes import main

from pylablib.devices import Basler


class DAQ_2DViewer_BaslerPLL(DAQ_2DViewer_GenericPylablibCamera):
    """
    """
    # Generate a  **list**  of available cameras. Only get the names
    camera_list = Basler.list_cameras(desc=False)

    # Update the params (nothing to change here)
    params = DAQ_2DViewer_GenericPylablibCamera.params
    params += {'title': 'Gain', 'name': 'gain', 'type': 'float', 'value': 1.0, 'readonly': False, 'default': 1.0},

    params[next((i for i, item in enumerate(params) if item["name"] == "camera_list"), None)]['limits'] = camera_list

    gain_name = None

    def init_controller(self):
        # Init camera with currently selected name
        camera = Basler.BaslerPylonCamera(name=self.params["camera_list"])

        # Handle the gain (behaves differently depending on camera)
        if "Gain" in camera.attributes:
            self.settings.child("gain").setOpts(title="Gain (dB)")
            self.settings.child("gain").setOpts(type="float")
            self.gain_name = "Gain"
        elif "GainRaw" in camera.attributes:
            self.settings.child("gain").setOpts(title="Gain")
            self.settings.child("gain").setOpts(type="int")
            self.settings.child("gain").setValue(int(self.settings["gain"]))
            self.gain_name = "GainRaw"
        else:
            self.settings.child("gain").hide()

        return camera

    def commit_settings(self, param):
        if param.name() == "exposure_time":
            exp = self.set_exposure(param.value() / 1000)
            self.settings.child("timing_opts", "exposure_time").setValue(exp * 1000)
        elif param.name() == "gain":
            self.controller.cav[self.gain_name] = param.value()
            self.settings.child("gain").setValue(self.controller.cav[self.gain_name])
        else:
            super().commit_settings(param)

    def set_exposure(self, exposure):
        """
        Sets the exposure of the camera
        The class does not use directly the pylablib function because it does not cover cameras
        with "ExposureTime" as attribute
        We use microseconds here like in pylon
        """
        if "ExposureTime" in self.controller.attributes:
            self.controller.cav["ExposureTime"] = exposure * 1E6
        else:
            self.controller.set_exposure(exposure)
        return self.get_exposure()

    def get_exposure(self):
        """
        Gets the exposure of the camera
        The class does not use directly the pylablib function because it does not cover cameras
        with "ExposureTime" as attribute
        """
        exp = self.get_attribute_value("ExposureTime", error_on_missing=False)
        if exp is not None:
            return exp / 1e6
        else:
            self.controller.get_exposure()

if __name__ == '__main__':
    main(__file__)

"""Class handle specific platform light."""
from inelsmqtt.devices import Device


class InelsLight(Device):
    """Carry light stuff

    Args:
        Device (_type_): it base class for all platforms
    """

    def set_ha_value(self, value: bool) -> bool:
        """Convert set value to the proper light object."""
        # new object passing into the device set func Device value object
        return super().set_ha_value(value)

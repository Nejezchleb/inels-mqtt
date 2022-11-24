"""Class handle specific platform switch."""
from inelsmqtt.devices import Device
from inelsmqtt.util import new_object


class InelsSwitch(Device):
    """Carry switch stuff

    Args:
        Device (_type_): it base class for all platforms
    """

    def set_ha_value(self, value: bool) -> bool:
        """Convert set value to the proper switch object."""
        # basic property is on
        kwargs = {"on": value}

        # other properties will be created from features
        for feature in self.features:
            kwargs[feature] = self.state.__dict__.get(feature)

        # new object passing into the device set func Device value object
        return super().set_ha_value(new_object(**kwargs))

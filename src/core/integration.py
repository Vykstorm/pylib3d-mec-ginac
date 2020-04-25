'''
Author: Víctor Ruiz Gómez
Description: This script defines the class IntegrationMethod and its subclasses
'''


######## Import statements ########




######## class IntegrationMethod ########

class NumericIntegration:
    @staticmethod
    def euler(q_values, dq_values, ddq_values, delta_t):
        '''
        This function performs the integration of the numeric values of the
        given coordinate variables ( and its derivatives ) using the
        euler method
        '''
        q_values += delta_t * (dq_values + 0.5 * delta_t * ddq_values)
        dq_values += delta_t * ddq_values


    @staticmethod
    def rk4(q_values, dq_values, ddq_values, delta_t):
        '''
        This function performs the integration of the numeric values of the
        given coordinate variables ( and its derivatives ) using the
        Range Kutta Order 4 algorithm
        '''
        # To be developed
        raise NotImplementedError


    @staticmethod
    def get_method(name):
        '''
        This function returns a integration function given its name.

        :param name: Name of the integration method to return
        :returns: The integration method
        '''
        if not isinstance(name, str):
            raise TypeError('Input argument should be a string')
        try:
            value = getattr(NumericIntegration, name.lower())
            if not callable(value):
                raise Exception
            return value
        except:
            raise IndexError(f'No integration method called "{name}"')

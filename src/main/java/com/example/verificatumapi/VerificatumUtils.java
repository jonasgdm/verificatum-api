package com.example.verificatumapi;

import com.verificatum.ui.info.Info;
import com.verificatum.ui.info.InfoException;

import java.util.ListIterator;

public class VerificatumUtils {

    /**
     * Clears all existing values of a field and inserts the new one.
     *
     * @param info      The info object (e.g. PartyInfo or PrivateInfo)
     * @param tag       The name of the XML field to override
     * @param newValue  The new value to insert
     * @throws InfoException If the value cannot be parsed or inserted
     */
    public static void overrideValue(Info info, String tag, String newValue) throws InfoException {
        ListIterator<Object> it = info.getValues(tag);
        while (it.hasNext()) {
            it.next();
            it.remove();
        }
        info.addValue(tag, newValue);
    }
}

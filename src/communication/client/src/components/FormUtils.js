class FormUtils {

    PERCENT = "percent";
    FREE_PER_X = "free_per_x"
    UP_TO_DATE = "up_to_date"
    OVERALL_PRODUCT_PRICE = "overall_product_price"
    OVERALL_CATEGORY_QUANTITY = "overall_category_quantity"
    OVERALL_CATEGORY_PRICE = "overall_category_price"
    OVERALL_PRODUCT_QUANTITY = "overall_product_quantity"
    BASKET_SIZE = "basket_size"
    BASKET_SIZE_INVALID = "Basket size expected to be non-negative"

    OVERALL_CATEGORY_QUANTITY_INVALID = "Expected format of name1:int1,name:int2 where int_i >= 0"
    PERCENT_INVALID = "Expected 1 to 100";
    FREE_PER_X_INVALID = "Expected simple fraction, such as 1/3 which means 1 free if you buy 3"
    OVERALL_PRODUCT_PRICE_INVALID = "Expected format of name1:int1,name:int2 where int_i >= 0"
    OVERALL_PRODUCT_QUANTITY_INVALID = "Expected format of name1:int1,name:int2 where int_i >= 0"
    OVERALL_CATEGORY_PRICE_INVALID = "Expected format of name1:int1,name:int2 where int_i >= 0"
    UP_TO_DATE_INVALID = "Expected full date d/m/y"
    UP_TO_DATE_EMPTY = "Up to date cannot be empty";
    START_DATE = "start_date"
    END_DATE = "end_date"
    INVALID_START_DATE = "invalid start date"
    INVALID_END_DATE = "invalid end date"

    STORENAME = "storename";
    STORE_NAME_INVALID = "Store name cannot contain @#!%^*+=._ characters, or spaces"
    PRODUCT_NAME_INVALID = "product name cannot contain @#!%^*+=._ characters, or spaces"
    STORE_NAME_EMPTY = "Store name cannot be empty";
    PRODUCT_NAME_EMPTY = "Product name cannot be empty";
    CATEGORY_EMPTY = "Category name cannot be empty";
    PRODUCT_NAME = "product_name";
    STORES_NAMES = "stores_names";
    BRANDS = "brands";
    BRAND = "brand";
    BRANDS_NAME_INVALID = "brand cannot contain @#!%^*+=._ characters, or spaces"
    CCV = "ccv";
    CCV_INVALID = "Invalid ccv"
    CREDIT_CARD = "credit_card";
    COUNTRY = "country";
    COUNTRY_INVALID = "Invalid Country Name";
    EXPIRY_DATE = "expiry_date";
    EXPIRY_DATE_INVALID = "Invalid Expiry Date";
    STREET = "street";
    STREET_INVALID = "Invalid street Name";
    CITY = "city";
    CITY_INVALID = "Invalid City Name";
    HOUSE_NUMBER = 'house_number';
    HOUSE_NUMBER_INVALID = "Invalid house number";
    APARTMENT = "apartment";
    APARTMENT_INVALID = "Invalid apartment identifier";
    FLOOR = "floor";
    FLOOR_INVALID = "Invalid floor number";
    CREDIT_CARD_INVALID = "credit card must contain 16 digits only";
    CATEGORIES = "categories";
    CATEGORY = "category";
    CATEGORY_INVALID = "category name cannot contain @#!%^*+=._ characters, or spaces"
    CATEGORIES_INVALID = "category cannot contain @#!%^*+=._ characters, or spaces"
    USERNAME = "username";
    EMAIL = "email";
    PASS1 = "pass1";
    PASS2 = "pass2";
    IS_VALID = 'is_valid';
    USER_NAME_EMPTY = "Username cannot be empty";
    USER_NAME_INVALID = "Username cannot contain @#!%^*+=._ characters, or spaces";
    EMAIL_INVALID = "Invalid email address";
    EMAIL_EMPTY = "Email cannot be empty";
    PASS1_EMPTY = "Password cannot be empty";
    PASS_NOT_LONG_ENOUGH = "Password needs to be at least 8 characters";
    PASS1_NOT_GOOD_ENOUGH = "Password must contain capital letter, non capital letter, digit, special character";
    PASS2_EMPTY = "Please Confirm your password";
    PASS2_NOT_MATCH = "Passwords not matched";
    PASS_MIN_LENGTH = 8;

    no_spaces_reg = new RegExp("^((?! ).)*$");
    address_reg = new RegExp("^[a-zA-Z\\s]*$");
    // address_reg = new RegExp(" /^[a-zA-Z\\s]*$/");
    no_special_chars = new RegExp("^(?=[a-zA-Z0-9]+$)(?!.*[_.]{2})[^_.].*[^_.]$");
    no_special_chars2 = new RegExp("^(?=[a-zA-Z0-9]+$)"); //(?!.*[_.]{2})[^_.].*[^_.]$");
    email_reg = new RegExp("^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$");
    strong_pass_regex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
    only_letter_digit_comma = new RegExp("^[a-zA-Z0-9,. ]*$");
    credit_card_reg = new RegExp("^\\d{16}$")
    ccv_reg = new RegExp("^\\d{3}$")
    expiry_date_reg = new RegExp("^(0[1-9]|1[012])\\/\\d{2}$")
    between_1_to_99 = new RegExp("^([1-9]|[1-9][0-9])$");
    free_per_x = new RegExp("^([1-9][0-9]*)\\/([1-9][0-9]*)$");
    name_number = new RegExp("^((([a-zA-Z0-9]+)\:([1-9][0-9]*))\,?)+$")
    name_float = new RegExp("^(([a-zA-Z0-9]+):([-+]*\\d+\\.\\d+|[-+]*\\d+),?)+$")
    full_date = new RegExp("^\\d{1,2}\\/\\d{1,2}\\/\\d{4}$")
    none_negative = new RegExp("^\\d+$")
    // date_reg = new RegExp("^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])[-.](19|20)\\d\\d$");
    // date_reg = new RegExp("/^\\d{1,2}\\/\\d{1,2}\\/\\d{4}$/")

    validate_new_store(storename) {
        let errors = FormUtils.defaultStoreNameDictionary();
        let is_storename = this.validate_storename(storename, errors)
        errors[this.IS_VALID] = is_storename;
        return errors;
    }


    validate_new_store_owner(username) {
        let errors = FormUtils.defaultUsernameDictionary();
        let is_username = this.validate_username(username, errors)
        errors[this.IS_VALID] = is_username;
        return errors;
    }

    validate_new_store_manager(username) {
        let errors = FormUtils.defaultUsernameDictionary();
        let is_username = this.validate_username(username, errors)
        errors[this.IS_VALID] = is_username;
        return errors;
    }

    validate_storename(storename, errors) {
        let is_valid = true;
        errors[this.STORENAME] = ""
        if (storename === "") {
            errors[this.STORENAME] = this.STORE_NAME_EMPTY;
            is_valid = false;

        } else if ((!(this.no_spaces_reg.test(storename))) || (!(this.no_special_chars.test(storename)))) {
            errors[this.STORENAME] = this.STORE_NAME_INVALID;
            is_valid = false;
        }
        return is_valid;
    }


    validate_category_for_adding(category, errors) {
        let is_valid = true;
        errors[this.CATEGORY] = ""
        if (category === "") {
            errors[this.CATEGORY] = this.CATEGORY_EMPTY;
            is_valid = false;
        } else if ((!(this.no_spaces_reg.test(category))) || (!(this.no_special_chars.test(category)))) {
            errors[this.CATEGORY] = this.CATEGORY_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_category_for_policy(category, errors) {
        let is_valid = true;
        errors[this.CATEGORY] = ""
        if (category !== "") {
            if ((!(this.no_spaces_reg.test(category))) || (!(this.no_special_chars.test(category)))) {
                errors[this.CATEGORY] = this.CATEGORY_INVALID;
                is_valid = false;
            }
        }
        return is_valid;
    }


    validate_product_name_for_adding(product_name, errors) {
        let is_valid = true;
        errors[this.PRODUCT_NAME] = ""
        if (product_name === "") {
            errors[this.PRODUCT_NAME] = this.PRODUCT_NAME_EMPTY;
            is_valid = false;
        } else if ((!(this.no_spaces_reg.test(product_name))) || (!(this.no_special_chars.test(product_name)))) {
            errors[this.PRODUCT_NAME] = this.PRODUCT_NAME_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_product_name_for_policy(product_name, errors) {
        let is_valid = true;
        errors[this.PRODUCT_NAME] = ""
        if (product_name !== "") {
            if ((!(this.no_spaces_reg.test(product_name))) || (!(this.no_special_chars.test(product_name)))) {
                errors[this.PRODUCT_NAME] = this.PRODUCT_NAME_INVALID;
                is_valid = false;
            }
        }
        return is_valid;
    }

    validate_brand_for_adding(brand, errors) {
        let is_valid = true;
        if (brand !== "") {
            if ((!(this.no_spaces_reg.test(brand))) || (!(this.only_letter_digit_comma.test(brand)))) {
                errors[this.BRAND] = this.BRANDS_NAME_INVALID;
                is_valid = false;
            }
        }
        return is_valid;
    }

    validate_categories_for_adding(categories, errors) {
        let is_valid = true;
        if (categories !== "") {
            if ((!(this.no_spaces_reg.test(categories))) || (!(this.only_letter_digit_comma.test(categories)))) {
                errors[this.CATEGORIES] = this.CATEGORIES_INVALID;
                is_valid = false;
            }
        }
        return is_valid;
    }

    validate_credit_card(credit_card, errors) {
        let is_valid = true;
        if (credit_card !== "") {
            if (!this.credit_card_reg.test(credit_card)) {
                errors[this.CREDIT_CARD] = this.CREDIT_CARD_INVALID;
                is_valid = false
            }
        }
        return is_valid;
    }

    validate_address_item(to_validate, errors, errors_field, error_msg) {
        let is_valid = true;
        if (to_validate !== "") {
            if (!this.address_reg.test(to_validate)) {
                errors[errors_field] = error_msg
                is_valid = false
            }

        } else if (to_validate === "" || to_validate === null) {
            errors[errors_field] = error_msg
            is_valid = false
        }
        return is_valid;
    }

    validate_apartment(apartment, errors) {
        let is_valid = true;
        if (apartment === "" || apartment === null) {
            return true
        } else if (!this.address_reg.test(apartment)) {
            errors[this.APARTMENT] = this.APARTMENT_INVALID
            is_valid = false
        }
        return is_valid;
    }

    validate_country(country, errors) {
        return this.validate_address_item(country, errors, this.COUNTRY, this.COUNTRY_INVALID)
    }

    validate_city(city, errors) {
        return this.validate_address_item(city, errors, this.CITY, this.CITY_INVALID)
    }

    validate_street(street, errors) {
        return this.validate_address_item(street, errors, this.STREET, this.STREET_INVALID)
    }

    validate_house_number(house_number, errors) {
        let is_valid = true;
        if ((house_number === "") || house_number === null) {
            return false;
        } else if (!this.none_negative.test(house_number)) {
            errors[this.HOUSE_NUMBER] = this.HOUSE_NUMBER_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_floor(floor, errors) {
        let is_valid = true;
        if ((floor === "") || floor === null) {
            return is_valid
        } else if (!this.none_negative.test(floor)) {
            errors[this.FLOOR] = this.FLOOR_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_ccv(ccv, errors){
        let is_valid = true;
        if ((ccv === "") || ccv === null) {
            return false;
        }
        if (!this.ccv_reg.test(ccv)) {
            errors[this.CCV] = this.CCV_INVALID
            is_valid = false;
        }
        return is_valid;
    }

    validate_expiry_date(expiry_date, errors)
    {
        let is_valid = true;
        if ((expiry_date === "") || expiry_date === null) {
            return false;
        }
        if (!this.expiry_date_reg.test(expiry_date)) {
            errors[this.EXPIRY_DATE] = this.EXPIRY_DATE_INVALID
            is_valid = false;
        }
        return is_valid;
    }

    validate_purchase_items(credit_card, country, city, street, house_number, apartment, floor, ccv, holder, holder_id, expiry_date) {
        let errors = FormUtils.defaultPurchaseItemsDictionary();
        let is_credit_card = this.validate_credit_card(credit_card, errors);
        let is_country = this.validate_country(country, errors)
        let is_city = this.validate_city(city, errors)
        let is_street = this.validate_street(street, errors)
        let is_house_number = this.validate_house_number(house_number, errors)
        let is_apartment = this.validate_apartment(apartment, errors)
        let is_floor = this.validate_floor(floor, errors)
        let is_ccv = this.validate_ccv(ccv, errors)
        let is_expiry_date = this.validate_expiry_date(expiry_date, errors)
        errors[this.IS_VALID] = is_credit_card && is_country && is_city && is_street && is_house_number && is_apartment && is_floor
            && is_ccv && is_expiry_date
        return errors;
    }


    validate_storeName_for_search(storeName, errors) {
        let is_valid = true;
        errors[this.STORENAME] = ""
        if (storeName.trim() === "") {
            return true;

        } else if (!(this.no_special_chars2.test(storeName))) {
            errors[this.STORENAME] = this.STORE_NAME_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_productName_for_search(productName, error) {
        let is_valid = true;
        error[this.PRODUCT_NAME] = "";
        if (!(this.no_special_chars.test(productName))) {
            error[this.PRODUCT_NAME] = this.PRODUCT_NAME_INVALID;
            is_valid = false;
        }
        return is_valid;
    }


    validate_overall_product_price(overall_price, errors) {
        errors[this.OVERALL_PRODUCT_PRICE] = "";
        try {
            if (overall_price === "") {
                return true;
            }
            if (!this.name_float.test(overall_price)) {
                errors[this.OVERALL_PRODUCT_PRICE] = this.OVERALL_PRODUCT_PRICE_INVALID;
                return false;
            }
            return true;
        } catch (e) {
        }
        errors[this.OVERALL_PRODUCT_PRICE] = this.OVERALL_PRODUCT_PRICE_INVALID;
        return false;
    }

    validate_overall_category_price(overall_price, errors) {
        errors[this.OVERALL_CATEGORY_PRICE] = "";
        try {
            if (overall_price === "") {
                return true;
            }
            if (!this.name_float.test(overall_price)) {
                errors[this.OVERALL_CATEGORY_PRICE] = this.OVERALL_CATEGORY_PRICE_INVALID;
                return false;
            }
            return true;
        } catch (e) {
        }
        errors[this.OVERALL_CATEGORY_PRICE] = this.OVERALL_CATEGORY_PRICE_INVALID;
        return false;
    }

    validate_overall_category_quantity(overall_quantity, errors) {
        errors[this.OVERALL_CATEGORY_QUANTITY] = "";
        try {
            if (overall_quantity === "") {
                return true;
            }
            if (!this.name_number.test(overall_quantity)) {
                errors[this.OVERALL_CATEGORY_QUANTITY] = this.OVERALL_CATEGORY_QUANTITY_INVALID;
                return false;
            }
            return true;
        } catch (e) {
        }
        errors[this.OVERALL_CATEGORY_QUANTITY] = this.OVERALL_CATEGORY_QUANTITY_INVALID;
        return false;
    }

    validate_overall_product_quantity(overall_quantity, errors) {
        errors[this.OVERALL_PRODUCT_QUANTITY] = "";
        try {
            if (overall_quantity === "") {
                return true;
            }
            if (!this.name_number.test(overall_quantity)) {
                errors[this.OVERALL_PRODUCT_QUANTITY] = this.OVERALL_PRODUCT_QUANTITY_INVALID;
                return false;
            }
            return true;
        } catch (e) {
        }
        errors[this.OVERALL_PRODUCT_QUANTITY] = this.OVERALL_PRODUCT_QUANTITY_INVALID;
        return false;
    }

    validate_up_to_date(up_to_date, errors) {
        errors[this.UP_TO_DATE] = ""
        if (up_to_date === "") {
            errors[this.UP_TO_DATE] = this.UP_TO_DATE_EMPTY;
            return false;
        }
        if (!this.full_date.test(up_to_date)) {
            errors[this.UP_TO_DATE] = this.UP_TO_DATE_INVALID;
            return false;
        }
        return true;
    }

    validate_basket_size(basket_size, errors) {
        let is_valid = true;
        errors[this.BASKET_SIZE] = ""
        if (basket_size.trim() === "") {
            return true;

        } else if (!(this.none_negative.test(basket_size))) {
            errors[this.BASKET_SIZE] = this.BASKET_SIZE_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_new_discount(free_per_x, percent, category, product_name, overall_product_price, overall_category_price, overall_product_quantity, overall_category_quantity, up_to_date, basket_size) {
        let errors = FormUtils.defaultAddDiscountDictionary();
        let is_product_name = this.validate_product_name_for_adding(product_name, errors);
        let is_category = this.validate_category_for_adding(category, errors);
        let is_free_per_x = this.validate_free_per_x(free_per_x, errors);
        let is_percent = this.validate_add_discount_percent(percent, errors);
        let is_overall_product_price = this.validate_overall_product_price(overall_product_price, errors)
        let is_overall_category_price = this.validate_overall_category_price(overall_category_price, errors)
        let is_overall_product_quantity = this.validate_overall_product_quantity(overall_product_quantity, errors)
        let is_overall_category_quantity = this.validate_overall_category_quantity(overall_category_quantity, errors)
        let is_up_to_date = this.validate_up_to_date(up_to_date, errors)
        let is_basket_size = this.validate_basket_size(basket_size, errors)
        errors[this.IS_VALID] = is_product_name && is_category && is_free_per_x && is_percent && is_overall_category_price && is_overall_product_price && is_overall_category_quantity && is_overall_product_quantity && is_up_to_date && is_basket_size;
        return errors;
    }

    validate_new_policy(product_name, category) {
        let errors = FormUtils.defaultPolicyDictionary();
        let is_product_name = this.validate_product_name_for_policy(product_name, errors);
        let is_category = this.validate_category_for_policy(category, errors);
        errors[this.IS_VALID] = is_product_name && is_category
        return errors;
    }

    validate_new_product(product_name, brand, categories) {
        let errors = FormUtils.defaultSearchProductDictionary();
        let is_product_name = this.validate_product_name_for_adding(product_name, errors);
        let is_brand = this.validate_brand_for_adding(brand, errors);
        let is_categories = this.validate_categories_for_adding(categories, errors);
        errors[this.IS_VALID] = is_product_name && is_brand && is_categories;
        return errors;
    }

    validate_positive_number(quantity, errors, type, error_msg) {
        if (quantity < 0) {
            errors[type] = error_msg
            return false
        }
        return true;
    }

    validate_edit_product(brand, categories, quantity, price) {
        let errors = FormUtils.defaultSearchProductDictionary();
        let is_brand = this.validate_brand_for_adding(brand, errors);
        let is_categories = this.validate_categories_for_adding(categories, errors);
        let is_quantity = this.validate_positive_number(quantity, errors, "quantity", "Must be a positive number")
        let is_price = this.validate_positive_number(price, errors, "price", "Must be a positive number")
        errors[this.IS_VALID] = is_brand && is_categories && is_quantity && is_price;
        return errors;
    }

    validate_register(username, email, pass1, pass2) {
        let errors = FormUtils.defaultRegisterDictionary();
        let is_username = this.validate_username(username, errors)
        let is_email = this.validate_email(email, errors)
        let is_pass1 = this.validate_password(pass1, errors)
        let is_pass2 = this.confirm_passwords(pass1, pass2, errors);
        errors[this.IS_VALID] = is_username && is_email && is_pass1 && is_pass2;
        return errors;
    }

    validate_login(username, pass1) {
        let errors = FormUtils.defaultRegisterDictionary();
        let is_username = this.validate_username(username, errors)
        let is_pass1 = this.validate_password(pass1, errors)
        errors[this.IS_VALID] = is_username && is_pass1
        return errors;
    }

    validate_store_search(store_name) {
        let errors = FormUtils.defaultSearchStoresDictionary();
        errors[this.IS_VALID] = this.validate_storeName_for_search(store_name, errors);
        return errors
    }

    validate_free_per_x(free_per_x, errors) {
        let is_valid = true;
        errors[this.FREE_PER_X] = ""
        if (!this.free_per_x.test(free_per_x)) {
            errors[this.FREE_PER_X] = this.FREE_PER_X_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_add_discount_percent(percent, errors) {
        let is_valid = true;
        errors[this.PERCENT] = ""
        if (!(this.between_1_to_99.test(percent))) {
            errors[this.PERCENT] = this.PERCENT_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_store_name(storeName, errors) {
        let is_valid = true;
        errors[this.STORENAME] = ""
        if (storeName === "") {
            return is_valid
        } else if (!(this.no_special_chars.test(storeName))) {
            errors[this.STORENAME] = this.STORE_NAME_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_username(username, errors) {
        let is_valid = true;
        errors[this.USERNAME] = ""

        if (username === "") {
            errors[this.USERNAME] = this.USER_NAME_EMPTY;
            is_valid = false;

        } else if ((!(this.no_spaces_reg.test(username))) || (!(this.no_special_chars.test(username)))) {
            errors[this.USERNAME] = this.USER_NAME_INVALID;
            is_valid = false;

        }
        return is_valid;
    }


    validate_email(email, errors) {
        let is_valid = true;
        errors[this.EMAIL] = ""

        if (email === "") {
            errors[this.EMAIL] = this.EMAIL_EMPTY;
            is_valid = false;
        } else if (!this.email_reg.test(email)) {
            errors[this.EMAIL] = this.EMAIL_INVALID;
            is_valid = false;
        }
        return is_valid;
    }

    validate_password(pass1, errors) {
        let is_valid = true;
        errors[this.PASS1] = ""
        if (pass1 === "") {
            errors[this.PASS1] = this.PASS1_EMPTY;
            is_valid = false;

        } else {
            if (!this.strong_pass_regex.test(pass1)) {
                errors[this.PASS1] = `${this.PASS1_NOT_GOOD_ENOUGH}\n`;
                is_valid = false;

            }
            if (pass1.length < this.PASS_MIN_LENGTH) {
                errors[this.PASS1] += this.PASS_NOT_LONG_ENOUGH;
                is_valid = false;

            }
        }
        return is_valid;
    }

    confirm_passwords(pass1, pass2, errors) {
        let is_valid = true;
        errors["pass2"] = ""
        if (pass2 === "") {
            errors[this.PASS2] = this.PASS2_EMPTY;
            is_valid = false;
        } else if (pass2 !== pass1) {
            errors[this.PASS2] = this.PASS2_NOT_MATCH;
            is_valid = false;
        }
        return is_valid;
    }

    validate_search_products(categories, product_name, stores_names, brands, min_price, max_price) {
        let errors = FormUtils.defaultSearchProductDictionary();
        let valid_product = true;
        let valid_store = true;
        let valid_price = true;
        let valid_brand = true;
        let valid_categories = true;
        errors[this.IS_VALID] = true;
        if (product_name === "") {
            errors[this.PRODUCT_NAME] = this.PRODUCT_NAME_EMPTY;
            valid_product = false
        } else if (!(this.no_special_chars.test(product_name))) {
            errors[this.PRODUCT_NAME] = this.PRODUCT_NAME_INVALID;
            valid_product = false;
        }
        // errors[this.IS_VALID] = min_price <= max_price;
        if( min_price > max_price){
            valid_price = false;
        }
        if (stores_names !== "" && !(this.no_special_chars2.test(stores_names))) {
            errors[this.STORES_NAMES] = this.STORE_NAME_INVALID;
            valid_store = false;
        }
        if (brands !== "" && !(this.no_special_chars2.test(brands))) {
            errors[this.BRANDS] = this.BRANDS_NAME_INVALID;
            valid_brand = false;
        }
        if (categories !== "" && !(this.no_special_chars2.test(categories))) {
            errors[this.CATEGORIES] = this.CATEGORIES_INVALID;
            valid_categories = false;
        }
        errors[this.IS_VALID] = valid_product & valid_store & valid_price & valid_brand & valid_categories;
        return errors
    }

    validate_start_date(start_date, errors){
        let is_valid = true;
        if (start_date !== "") {
            if(!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(start_date)){
                errors[this.START_DATE] = this.INVALID_START_DATE;
                is_valid = false
            }
            else{
                var dateParts = start_date.split("/");
                var date_obj = new Date(dateParts[1]+"/"+dateParts[0]+"/"+dateParts[2])
                is_valid = date_obj instanceof Date && !isNaN(date_obj)
                if (!is_valid){
                    errors[this.START_DATE] = this.INVALID_START_DATE;
                }
            }

        }
        return is_valid;
    }

        validate_end_date(end_date, errors){
        let is_valid = true;
        if (end_date !== "") {
            if(!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(end_date)){
                errors[this.END_DATE] = this.INVALID_END_DATE;
                is_valid = false
            }
            else{
                var dateParts = end_date.split("/");
                var date_obj = new Date(dateParts[1]+"/"+dateParts[0]+"/"+dateParts[2])
                is_valid = date_obj instanceof Date && !isNaN(date_obj)
                if (!is_valid){
                    errors[this.END_DATE] = this.INVALID_END_DATE;
                }
            }
        }

        return is_valid;
    }

    validate_dates(start_date, end_date){
        let errors = FormUtils.defaultViewStats();
        let is_valid_start_date = this.validate_start_date(start_date, errors)
        let is_valid_end_date = this.validate_end_date(end_date, errors)
        errors[this.IS_VALID] = ((is_valid_start_date && is_valid_end_date) &&
            this.compare(start_date, end_date) <= 0)
        return errors
    }

    compare(date1, date2){
        var split1 = date1.split('/')
        var split2 = date2.split('/')
        var y1 = parseInt(split1[2], 10)
        var y2 = parseInt(split2[2], 10)
        var m1 = parseInt(split1[1], 10)
        var m2 = parseInt(split2[1], 10)
        var d1 = parseInt(split1[0], 10)
        var d2 = parseInt(split2[0], 10)
        if (y1 < y2){
            return -1
        }
        else if(y1 > y2){
            return 1
        }
        else{
            if (m1 < m2){
                return -1
            }
            else if(m1 > m2){
                return 1
            }
            else{
                if (d1 < d2){
                    return -1
                }
                else if(d1 > d2){
                    return 1
                }
                else{
                    return 0
                }
            }
        }

    }


    static defaultStoreNameDictionary() {
        return {
            is_valid: false,
            storename: ""
        }
    }

    static defaultAddProductDictionary() {
        return {
            is_valid: false,
            product_name: "",
            brand: "",
            categories: ""
        }
    }

    static defaultRegisterDictionary() {
        return {
            is_valid: false,
            username: "",
            email: "",
            pass1: "",
            pass2: "",
        }
    }

    static defaultLoginDictionary() {
        return {
            is_valid: false,
            username: "",
            pass1: "",
        }
    }

    static defaultPolicyDictionary() {
        return {
            is_valid: false,
            product_name: "",
            category: ""
        }
    }

    static defaultSearchProductDictionary() {
        return {
            is_valid: false,
            categories: "",
            product_name: "",
            stores_names: "",
            brands: "",
        }
    }

    static defaultSearchStoresDictionary() {
        return {
            is_valid: true,
            storename: "",
        }
    }

    static defaultNewManagerDictionary() {
        return {
            is_valid: false,
            storename: "",
            username: ""
        };
    }

    static defaultUsernameDictionary() {
        return {
            is_valid: false,
            username: ""
        }
    }

    static defaultEditProductDictionary() {
        return {
            is_valid: false,
            brand: "",
            categories: "",
            quantity: "",
            base_price: "",
        }
    }

    static defaultPurchaseItemsDictionary() {
        return {
            is_valid: false,
            credit_card: "",
            country: "",
            street: "",
            city: "",
            house_number: "",
            apartment: "",
            floor: "",
            ccv: "",
            holder: "",
            holder_id: "",
            expiry_date: ""
        }
    }

    static defaultAddDiscountDictionary() {
        return {
            is_valid: false,
            product_name: "",
            discount_type: "1",
            category: "",
            percent: "",
            free_per_x: "",
            overall_product_quantity: "",
            overall_category_quantity: "",
            overall_product_price: "",
            overall_category_price: "",
            up_to_date: "",
            basket_size: ""
        };
    }

    static defaultViewStats() {
        return {
            is_valid: false,
            start_date: "",
            end_date: ""
        };
    }

}

export default FormUtils;


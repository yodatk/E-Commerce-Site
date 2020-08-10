import React, {Component} from "react";
import {
    MDBBtn,
    MDBBtnGroup,
    MDBCol,
    MDBContainer,
    MDBInput,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead
} from "mdbreact";
import axios from "axios";
import {Link, withRouter} from "react-router-dom";
import FormUtils from "../FormUtils";
import * as HttpStatus from "http-status-codes";

class ManagePolicies extends Component {
    state = {
        policies: [],
        category: "",
        min_basket_quantity: "",
        max_basket_quantity: "",
        product_name: "",
        min_product_quantity: "",
        max_product_quantity: "",
        min_category_quantity: "",
        max_category_quantity: "",
        day: "",
        policy_type: "1",
        been_submitted: false,
        errors: FormUtils.defaultPolicyDictionary()
    };

    formUtils = new FormUtils();

    validateProductName = () => this.formUtils.validate_product_name_for_adding(this.state.product_name, this.state.errors);


    validateCategory = () => this.formUtils.validate_category_for_adding(this.state.category, this.state.errors);


    columns = [
        {
            label: '#',
            field: 'id',
            sort: 'asc'
        },
        {
            label: 'Policy id',
            field: 'policy_id',
            sort: 'asc'
        },
        {
            label: 'description',
            field: 'description',
            sort: 'asc'
        },
        {
            label: 'Edit',
            field: 'edit',
            sort: 'asc'
        }
    ];


    componentDidMount() {
        this.fetching();
    }

    fetching = () => {

        axios.get(
            "/fetch_policies/" + this.props.getUserId() + "/" + this.props.match.params.storename
        )
            .then((res) => {
                console.log(res)
                this.setState({policies: res.data !== null ? res.data.data : []});
            }).catch(error => {
            console.log(error)
        });
    }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
        this.forceUpdate()
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultPolicyDictionary()})
    }

    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/add_policies",
                {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename,
                    category: this.state.category,
                    min_basket_quantity: this.state.min_basket_quantity,
                    max_basket_quantity: this.state.max_basket_quantity,
                    product_name: this.state.product_name,
                    min_product_quantity: this.state.min_product_quantity,
                    max_product_quantity: this.state.max_product_quantity,
                    min_category_quantity: this.state.min_category_quantity,
                    max_category_quantity: this.state.max_category_quantity,
                    day: this.state.day
                },
            )
                .then((res) => {
                    console.log('Policy added', res)
                    this.dealWithRegisterResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithRegisterResult(error.response);
            });
        }
    }

    dealWithRegisterResult = (res) => {
        if (res) {
            console.log("arrived deal with in manage policies")
            if (res.status === HttpStatus.OK) {
                this.fetching()
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    };

    delete_policy = (policy_id) => {
        if (window.confirm("Are you sure?")) {
            axios.post(
                "/remove_policy",
                {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename,
                    policy_id: policy_id
                },
            )
                .then((res) => {
                    this.dealWithRegisterResult(res);
                }).catch(error => {
                this.dealWithRegisterResult(error.response);
            });
        } else {
            console.log('Say no')
        }
    };

    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = null;
        new_errors = this.formUtils.validate_new_policy(this.state.product_name, this.state.category);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);
        console.log('Submit', new_errors)
    };

    updatedRows = () => {
        console.log(Object.entries(this.state.policies));
        let res = [];
        let idCounter = 1;
        for (let policy of this.state.policies) {
            let dictInfo = {};
            dictInfo['id'] = idCounter;
            dictInfo['policy_id'] = policy['policy_id'];
            dictInfo['description'] = policy['description'];
            dictInfo['edit'] =
                <div>
                    <MDBBtnGroup size="md">
                        <MDBBtn color="warning" id="delete_button" onClick={() => {
                            this.delete_policy(dictInfo['policy_id'])
                        }}>Delete Policy</MDBBtn>
                    </MDBBtnGroup>
                    <MDBBtnGroup size="md">
                        <MDBBtn color="primary"><Link style={{'color': 'white'}}
                                                      to={`/edit_policy/${dictInfo['policy_id']}/${this.props.match.params.storename}`}>Edit
                            Policy</Link></MDBBtn>
                    </MDBBtnGroup>
                </div>;
            res.push(dictInfo);
            idCounter++;
        }
        return res;
    };

    renderProductsResults = () => {
        return <MDBContainer>
            <MDBTable responsive>
                <MDBTableHead color="default-color" columns={this.columns} textWhite/>
                <MDBTableBody rows={this.updatedRows()}/>
            </MDBTable>
        </MDBContainer>
    }


    render() {

        let category_input = null;
        let min_category_quantity_input = null;
        let max_category_quantity_input = null;

        let min_basket_quantity_input = null;
        let max_basket_quantity_input = null;

        let product_name_input = null;
        let min_product_quantity_input = null;
        let max_product_quantity_input = null;

        let day_input = null;

        if (this.state.policy_type === "3") {

            this.state.min_basket_quantity = "";
            this.state.max_basket_quantity = "";
            this.state.product_name = "";
            this.state.min_product_quantity = "";
            this.state.max_product_quantity = "";
            this.state.day = "";

            category_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.category}
                                  name="category"
                                  label="Category" icon="box" group type="text"
                                  className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["category"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
            min_category_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.min_category_quantity}
                                  name="min_category_quantity"
                                  label="Minimum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["min_category_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
            max_category_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.max_category_quantity}
                                  name="max_category_quantity"
                                  label="Maximum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["max_category_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
        } else if (this.state.policy_type === "2") {

            this.state.min_basket_quantity = "";
            this.state.max_basket_quantity = "";
            this.state.category = "";
            this.state.min_category_quantity = "";
            this.state.max_category_quantity = "";
            this.state.day = "";

            product_name_input = <div className="grey-text">
                <div className="form-group">
                    <MDBInput onChange={this.onChange} value={this.state.product_name}
                              name="product_name"
                              label="Product Name" icon="folder" group type="text"
                              className={this.state.been_submitted ? (this.validateProductName() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                              required
                              error="wrong"
                              success="right"/>
                    <div className="invalid-feedback"
                         style={{display: "block"}}>{this.state.errors["product_name"]}
                    </div>
                    <div className="valid-feedback"/>
                </div>
            </div>
            min_product_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.min_product_quantity}
                                  name="min_product_quantity"
                                  label="Minimum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["min_product_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
            max_product_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.max_product_quantity}
                                  name="max_product_quantity"
                                  label="Maximum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["max_product_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
        } else if (this.state.policy_type === "1") {

            this.state.category = "";
            this.state.min_category_quantity = "";
            this.state.max_category_quantity = "";
            this.state.day = "";
            this.state.product_name = "";
            this.state.min_product_quantity = "";
            this.state.max_product_quantity = "";

            min_basket_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.min_basket_quantity}
                                  name="min_basket_quantity"
                                  label="Minimum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["min_basket_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
            max_basket_quantity_input =
                <div className="grey-text">
                    <div className="form-group">
                        <MDBInput onChange={this.onChange} value={this.state.max_basket_quantity}
                                  name="max_basket_quantity"
                                  label="Maximum Quantity" icon="box" group type="number"
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                            // className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                  required
                                  error="wrong"
                                  success="right"/>
                        <div className="invalid-feedback"
                             style={{display: "block"}}>{this.state.errors["max_basket_quantity"]}
                        </div>
                        <div className="valid-feedback"/>
                    </div>
                </div>
        } else if (this.state.policy_type === "4") {

            this.state.category = "";
            this.state.min_category_quantity = "";
            this.state.max_category_quantity = "";
            this.state.product_name = "";
            this.state.min_product_quantity = "";
            this.state.max_product_quantity = "";
            this.state.min_basket_quantity = "";
            this.state.max_basket_quantity = "";

            day_input = <div>
                <br/>
                <p> Choose a day that purchase is not allowed</p>
                <br/>
                <select name="day" onChange={this.onChange} value={this.state.day}
                        className="browser-default custom-select">
                    <option>Choose a Day</option>
                    <option value="Sunday">Sunday</option>
                    <option value="Monday">Monday</option>
                    <option value="Tuesday">Tuesday</option>
                    <option value="Wednesday">Wednesday</option>
                    <option value="Thursday">Thursday</option>
                    <option value="Friday">Friday</option>
                    <option value="Saturday">Saturday</option>

                </select>
            </div>
        }
        return (
            <MDBContainer>
                <br/>
                <MDBRow
                    style={{
                        display: "flex",
                        alignItems: "right",
                        justifyContent: "right",
                    }}>
                    <MDBCol md="5">
                        <form className="needs-validation" onSubmit={(val) => {
                            this.onSubmit(val)
                        }} noValidate>
                            <p className="h3 text-center mb-4">Add Shopping Policy</p>
                            <div>
                                <select name="policy_type" onChange={this.onChange} value={this.state.policy_type}
                                        className="browser-default custom-select">
                                    <option value="1">Basket Policy</option>
                                    <option value="2">Product Policy</option>
                                    <option value="3">Category Policy</option>
                                    <option value="4">Weekday Policy</option>
                                </select>
                            </div>

                            {category_input}
                            {min_category_quantity_input}
                            {max_category_quantity_input}
                            {product_name_input}
                            {min_product_quantity_input}
                            {max_product_quantity_input}
                            {min_basket_quantity_input}
                            {max_basket_quantity_input}
                            {day_input}

                            <div className="text-center">
                                <MDBBtn type="submit"
                                        value="Submit"
                                        outline
                                        id="submit_button"
                                        color="info">Add</MDBBtn>
                            </div>
                        </form>
                        <p onChange={this.onChange} className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                    </MDBCol>
                    <MDBCol>
                        {this.renderProductsResults()}
                    </MDBCol>
                </MDBRow>


            </MDBContainer>
        );
    }

}

export default withRouter(ManagePolicies);
